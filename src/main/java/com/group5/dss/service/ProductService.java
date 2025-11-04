package com.group5.dss.service;

import com.group5.dss.model.ProductDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AddFieldsOperation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
import org.springframework.data.mongodb.core.aggregation.GroupOperation;
import org.springframework.data.mongodb.core.aggregation.MatchOperation;
import org.springframework.data.mongodb.core.aggregation.ConditionalOperators;
import org.springframework.data.mongodb.core.aggregation.ConvertOperators;
import org.springframework.data.mongodb.core.aggregation.ArithmeticOperators;
import org.springframework.data.mongodb.core.aggregation.ComparisonOperators;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;

@Service
public class ProductService {
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Get all products aggregated from invoices
     * Groups by stockCode and calculates statistics
     */
    public List<ProductDTO> getAllProducts() {
        // Normalize stock code for consistent grouping
        AddFieldsOperation normalizeStockCode = addFields()
            .addFieldWithValue("normalizedStockCode", ConvertOperators.ToString.toString("$StockCode"))
            .build();

        // Match only valid products (positive quantity and price)
        MatchOperation matchStage = match(
            new Criteria().andOperator(
                Criteria.where("Quantity").gt(0),
                Criteria.where("UnitPrice").gt(0),
                Criteria.where("StockCode").ne(null).ne("")
            )
        );
        
        // Group by stockCode and calculate aggregates
        GroupOperation groupStage = group("normalizedStockCode")
            .first("Description").as("description")
            .sum("Quantity").as("totalQuantitySold")
            .avg("UnitPrice").as("averagePrice")
            .count().as("totalTransactions")
            .min("UnitPrice").as("minPrice")
            .max("UnitPrice").as("maxPrice")
            .addToSet("CustomerID").as("customers")
            .sum("TotalPrice").as("totalRevenueFromTotalPrice");
        
        // Project to match ProductDTO structure and calculate revenue
        var projectStage = project()
            .and("_id").as("stockCode")
            .andInclude("description", "totalQuantitySold", 
                       "averagePrice", "totalTransactions", "minPrice", "maxPrice")
            .and("customers").size().as("uniqueCustomers")
            .and(
                ConditionalOperators.when(
                    ComparisonOperators.Eq.valueOf("totalRevenueFromTotalPrice").equalToValue(0)
                ).thenValueOf(
                    ArithmeticOperators.Multiply.valueOf("totalQuantitySold").multiplyBy("averagePrice")
                ).otherwiseValueOf("$totalRevenueFromTotalPrice")
            ).as("totalRevenue");
        
        // Sort by total revenue descending
        var sortStage = sort(Sort.by(Sort.Direction.DESC, "totalRevenue"));
        
        Aggregation aggregation = newAggregation(
            normalizeStockCode,
            matchStage,
            groupStage,
            projectStage,
            sortStage
        );
        
        AggregationResults<ProductDTO> results = mongoTemplate.aggregate(
            aggregation, "DSS", ProductDTO.class
        );
        
        return results.getMappedResults();
    }
    
    /**
     * Get product details by stock code
     */
    public Optional<ProductDTO> getProductByStockCode(String stockCode) {
        AddFieldsOperation normalizeStockCode = addFields()
            .addFieldWithValue("normalizedStockCode", ConvertOperators.ToString.toString("$StockCode"))
            .build();

        // Match specific product
        MatchOperation matchStage = match(
            new Criteria().andOperator(
                Criteria.where("normalizedStockCode").is(stockCode),
                Criteria.where("Quantity").gt(0),
                Criteria.where("UnitPrice").gt(0)
            )
        );
        
        // Group by stockCode and calculate aggregates
        GroupOperation groupStage = group("normalizedStockCode")
            .first("Description").as("description")
            .sum("Quantity").as("totalQuantitySold")
            .avg("UnitPrice").as("averagePrice")
            .count().as("totalTransactions")
            .min("UnitPrice").as("minPrice")
            .max("UnitPrice").as("maxPrice")
            .addToSet("CustomerID").as("customers")
            .sum("TotalPrice").as("totalRevenueFromTotalPrice");
        
        // Project to match ProductDTO structure and calculate revenue
        var projectStage = project()
            .and("_id").as("stockCode")
            .andInclude("description", "totalQuantitySold", 
                       "averagePrice", "totalTransactions", "minPrice", "maxPrice")
            .and("customers").size().as("uniqueCustomers")
            .and(
                ConditionalOperators.when(
                    ComparisonOperators.Eq.valueOf("totalRevenueFromTotalPrice").equalToValue(0)
                ).thenValueOf(
                    ArithmeticOperators.Multiply.valueOf("totalQuantitySold").multiplyBy("averagePrice")
                ).otherwiseValueOf("$totalRevenueFromTotalPrice")
            ).as("totalRevenue");
        
        Aggregation aggregation = newAggregation(
            normalizeStockCode,
            matchStage,
            groupStage,
            projectStage
        );
        
        AggregationResults<ProductDTO> results = mongoTemplate.aggregate(
            aggregation, "DSS", ProductDTO.class
        );
        
        return results.getMappedResults().stream().findFirst();
    }
    
    /**
     * Get total product count
     */
    public long getTotalProductCount() {
        return getAllProducts().size();
    }
    
    /**
     * Search products by description or stock code
     */
    public List<ProductDTO> searchProducts(String query) {
        AddFieldsOperation normalizeStockCode = addFields()
            .addFieldWithValue("normalizedStockCode", ConvertOperators.ToString.toString("$StockCode"))
            .build();

        MatchOperation matchStage = match(
            new Criteria().orOperator(
                Criteria.where("normalizedStockCode").regex(query, "i"),
                Criteria.where("Description").regex(query, "i")
            ).andOperator(
                Criteria.where("Quantity").gt(0),
                Criteria.where("UnitPrice").gt(0),
                Criteria.where("StockCode").ne(null).ne("")
            )
        );
        
        GroupOperation groupStage = group("normalizedStockCode")
            .first("Description").as("description")
            .sum("Quantity").as("totalQuantitySold")
            .avg("UnitPrice").as("averagePrice")
            .count().as("totalTransactions")
            .addToSet("CustomerID").as("customers")
            .sum("TotalPrice").as("totalRevenueFromTotalPrice");
        
        var projectStage = project()
            .and("_id").as("stockCode")
            .andInclude("description", "totalQuantitySold", 
                       "averagePrice", "totalTransactions")
            .and("customers").size().as("uniqueCustomers")
            .and(
                ConditionalOperators.when(
                    ComparisonOperators.Eq.valueOf("totalRevenueFromTotalPrice").equalToValue(0)
                ).thenValueOf(
                    ArithmeticOperators.Multiply.valueOf("totalQuantitySold").multiplyBy("averagePrice")
                ).otherwiseValueOf("$totalRevenueFromTotalPrice")
            ).as("totalRevenue");
        
        var sortStage = sort(Sort.by(Sort.Direction.DESC, "totalRevenue"));
        
        Aggregation aggregation = newAggregation(
            normalizeStockCode,
            matchStage,
            groupStage,
            projectStage,
            sortStage
        );
        
        AggregationResults<ProductDTO> results = mongoTemplate.aggregate(
            aggregation, "DSS", ProductDTO.class
        );
        
        return results.getMappedResults();
    }
}
