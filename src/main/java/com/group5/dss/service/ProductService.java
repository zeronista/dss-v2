package com.group5.dss.service;

import com.group5.dss.model.ProductDTO;
import com.group5.dss.model.Invoice;
import com.group5.dss.util.LocalDataLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class ProductService {
    
    @Autowired
    private LocalDataLoader localDataLoader;
    
    /**
     * Get all products aggregated from LOCAL CSV file
     * Groups by stockCode and calculates statistics
     * Using FULL dataset including cancelled orders for Admin role
     */
    public List<ProductDTO> getAllProducts() {
        System.out.println("📦 Loading products from FULL LOCAL CSV (including cancelled orders)...");
        
        List<Invoice> invoices = localDataLoader.loadFullTransactions();
        
        // Filter valid products (positive quantity and price)
        List<Invoice> validInvoices = invoices.stream()
                .filter(inv -> inv.getQuantity() != null && inv.getQuantity() > 0)
                .filter(inv -> inv.getUnitPrice() != null && inv.getUnitPrice() > 0)
                .filter(inv -> inv.getStockCode() != null && !inv.getStockCode().isEmpty())
                .collect(Collectors.toList());
        
        // Group by stock code
        Map<String, List<Invoice>> groupedByStockCode = validInvoices.stream()
                .collect(Collectors.groupingBy(Invoice::getStockCode));
        
        // Build product DTOs
        List<ProductDTO> products = new ArrayList<>();
        
        for (Map.Entry<String, List<Invoice>> entry : groupedByStockCode.entrySet()) {
            String stockCode = entry.getKey();
            List<Invoice> productInvoices = entry.getValue();
            
            ProductDTO product = buildProductDTO(stockCode, productInvoices);
            products.add(product);
        }
        
        // Sort by total revenue descending
        products.sort(Comparator.comparing(ProductDTO::getTotalRevenue).reversed());
        
        System.out.println("✅ Loaded " + products.size() + " products from FULL LOCAL CSV");
        return products;
    }
    
    /**
     * Get product details by stock code from LOCAL CSV
     * Using FULL dataset including cancelled orders for Admin role
     */
    public Optional<ProductDTO> getProductByStockCode(String stockCode) {
        System.out.println("📦 Loading product " + stockCode + " from FULL LOCAL CSV (including cancelled orders)...");
        
        List<Invoice> invoices = localDataLoader.loadFullTransactions();
        
        // Filter for this specific product
        List<Invoice> productInvoices = invoices.stream()
                .filter(inv -> stockCode.equals(inv.getStockCode()))
                .filter(inv -> inv.getQuantity() != null && inv.getQuantity() > 0)
                .filter(inv -> inv.getUnitPrice() != null && inv.getUnitPrice() > 0)
                .collect(Collectors.toList());
        
        if (productInvoices.isEmpty()) {
            return Optional.empty();
        }
        
        ProductDTO product = buildProductDTO(stockCode, productInvoices);
        System.out.println("✅ Found product: " + product.getDescription());
        
        return Optional.of(product);
    }
    
    /**
     * Search products by stock code or description from LOCAL CSV
     */
    public List<ProductDTO> searchProducts(String query) {
        System.out.println("🔍 Searching products in LOCAL CSV: " + query);
        
        List<ProductDTO> allProducts = getAllProducts();
        
        String queryLower = query.toLowerCase();
        return allProducts.stream()
                .filter(p -> 
                    p.getStockCode().toLowerCase().contains(queryLower) ||
                    (p.getDescription() != null && p.getDescription().toLowerCase().contains(queryLower))
                )
                .collect(Collectors.toList());
    }
    
    /**
     * Build ProductDTO from list of invoices
     */
    private ProductDTO buildProductDTO(String stockCode, List<Invoice> invoices) {
        ProductDTO product = new ProductDTO();
        product.setStockCode(stockCode);
        
        // Description (use first non-null)
        String description = invoices.stream()
                .map(Invoice::getDescription)
                .filter(Objects::nonNull)
                .findFirst()
                .orElse("No description");
        product.setDescription(description);
        
        // Total quantity sold
        long totalQuantity = invoices.stream()
                .mapToLong(inv -> inv.getQuantity() != null ? inv.getQuantity() : 0)
                .sum();
        product.setTotalQuantitySold(totalQuantity);
        
        // Average price
        double avgPrice = invoices.stream()
                .filter(inv -> inv.getUnitPrice() != null)
                .mapToDouble(Invoice::getUnitPrice)
                .average()
                .orElse(0.0);
        product.setAveragePrice(avgPrice);
        
        // Total transactions
        long totalTransactions = invoices.size();
        product.setTotalTransactions(totalTransactions);
        
        // Min and Max price
        double minPrice = invoices.stream()
                .filter(inv -> inv.getUnitPrice() != null)
                .mapToDouble(Invoice::getUnitPrice)
                .min()
                .orElse(0.0);
        product.setMinPrice(minPrice);
        
        double maxPrice = invoices.stream()
                .filter(inv -> inv.getUnitPrice() != null)
                .mapToDouble(Invoice::getUnitPrice)
                .max()
                .orElse(0.0);
        product.setMaxPrice(maxPrice);
        
        // Unique customers
        long uniqueCustomers = invoices.stream()
                .map(Invoice::getCustomerId)
                .filter(Objects::nonNull)
                .distinct()
                .count();
        product.setUniqueCustomers((int) uniqueCustomers);
        
        // Total revenue (use TotalPrice if available, otherwise calculate)
        double totalRevenue = invoices.stream()
                .mapToDouble(inv -> {
                    if (inv.getTotalPrice() != null && inv.getTotalPrice() != 0) {
                        return inv.getTotalPrice();
                    } else if (inv.getQuantity() != null && inv.getUnitPrice() != null) {
                        return inv.getQuantity() * inv.getUnitPrice();
                    }
                    return 0.0;
                })
                .sum();
        product.setTotalRevenue(totalRevenue);
        
        return product;
    }
}
