package com.group5.dss.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductDTO {
    
    private String stockCode;
    private String description;
    private Long totalQuantitySold;
    private Double totalRevenue;
    private Double averagePrice;
    private Long totalTransactions;
    private Integer uniqueCustomers;
    
    // For detail view
    private Double minPrice;
    private Double maxPrice;
    
    // Constructor for aggregation results
    public ProductDTO(String stockCode, String description, Long totalQuantitySold, 
                     Double totalRevenue, Double averagePrice, Long totalTransactions) {
        this.stockCode = stockCode;
        this.description = description;
        this.totalQuantitySold = totalQuantitySold;
        this.totalRevenue = totalRevenue;
        this.averagePrice = averagePrice;
        this.totalTransactions = totalTransactions;
    }
}
