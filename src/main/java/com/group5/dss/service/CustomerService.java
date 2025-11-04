package com.group5.dss.service;

import com.group5.dss.model.CustomerDTO;
import com.group5.dss.model.Invoice;
import com.group5.dss.util.LocalDataLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class CustomerService {
    
    @Autowired
    private LocalDataLoader localDataLoader;
    
    /**
     * Get all customers with aggregated statistics from LOCAL CSV
     */
    public List<CustomerDTO> getAllCustomers() {
        System.out.println("👥 Loading customers from LOCAL CSV...");
        
        // Get all invoices from local file
        List<Invoice> allInvoices = localDataLoader.loadCleanedTransactions();
        
        // Group by customer ID
        Map<Integer, List<Invoice>> invoicesByCustomer = allInvoices.stream()
                .filter(invoice -> invoice.getCustomerId() != null)
                .collect(Collectors.groupingBy(Invoice::getCustomerId));
        
        // Build customer DTOs
        List<CustomerDTO> customers = invoicesByCustomer.entrySet().stream()
                .map(entry -> buildCustomerDTO(entry.getKey(), entry.getValue()))
                .sorted(Comparator.comparing(CustomerDTO::getTotalRevenue).reversed())
                .collect(Collectors.toList());
        
        System.out.println("✅ Loaded " + customers.size() + " customers from LOCAL CSV");
        return customers;
    }
    
    /**
     * Get customer details by ID from LOCAL CSV
     */
    public Optional<CustomerDTO> getCustomerById(Integer customerId) {
        System.out.println("👤 Loading customer " + customerId + " from LOCAL CSV...");
        
        List<Invoice> allInvoices = localDataLoader.loadCleanedTransactions();
        List<Invoice> customerInvoices = allInvoices.stream()
                .filter(inv -> customerId.equals(inv.getCustomerId()))
                .collect(Collectors.toList());
        
        if (customerInvoices.isEmpty()) {
            return Optional.empty();
        }
        
        CustomerDTO customer = buildCustomerDTO(customerId, customerInvoices);
        System.out.println("✅ Found customer from " + customer.getCountry());
        
        return Optional.of(customer);
    }
    
    /**
     * Search customers by ID or country
     */
    public List<CustomerDTO> searchCustomers(String query) {
        List<CustomerDTO> allCustomers = getAllCustomers();
        
        return allCustomers.stream()
                .filter(customer -> 
                    customer.getCustomerId().toString().contains(query) ||
                    (customer.getCountry() != null && customer.getCountry().toLowerCase().contains(query.toLowerCase()))
                )
                .collect(Collectors.toList());
    }
    
    /**
     * Build CustomerDTO from list of invoices
     */
    private CustomerDTO buildCustomerDTO(Integer customerId, List<Invoice> invoices) {
        CustomerDTO dto = new CustomerDTO();
        dto.setCustomerId(customerId);
        
        // Filter valid invoices (non-cancelled)
        List<Invoice> validInvoices = invoices.stream()
                .filter(inv -> inv.getInvoiceNo() != null && !inv.getInvoiceNo().toString().startsWith("-"))
                .collect(Collectors.toList());
        
        // Filter returned/cancelled invoices
        List<Invoice> returnedInvoices = invoices.stream()
                .filter(inv -> inv.getInvoiceNo() != null && inv.getInvoiceNo().toString().startsWith("-"))
                .collect(Collectors.toList());
        
        // Country (use most common)
        String country = invoices.stream()
                .map(Invoice::getCountry)
                .filter(Objects::nonNull)
                .findFirst()
                .orElse("Unknown");
        dto.setCountry(country);
        
        // Order statistics
        long totalOrders = validInvoices.stream()
                .map(Invoice::getInvoiceNo)
                .distinct()
                .count();
        dto.setTotalOrders(totalOrders);
        
        long totalItems = validInvoices.stream()
                .mapToLong(inv -> inv.getQuantity() != null ? inv.getQuantity() : 0)
                .sum();
        dto.setTotalItems(totalItems);
        
        double totalRevenue = validInvoices.stream()
                .mapToDouble(inv -> {
                    if (inv.getTotalPrice() != null) {
                        return inv.getTotalPrice();
                    } else if (inv.getQuantity() != null && inv.getUnitPrice() != null) {
                        return inv.getQuantity() * inv.getUnitPrice();
                    }
                    return 0.0;
                })
                .sum();
        dto.setTotalRevenue(totalRevenue);
        
        dto.setAverageOrderValue(totalOrders > 0 ? totalRevenue / totalOrders : 0.0);
        
        // Unique products
        long uniqueProducts = validInvoices.stream()
                .map(Invoice::getStockCode)
                .filter(Objects::nonNull)
                .distinct()
                .count();
        dto.setUniqueProductsPurchased(uniqueProducts);
        
        // Dates
        Optional<String> firstDate = validInvoices.stream()
                .map(Invoice::getInvoiceDate)
                .filter(Objects::nonNull)
                .min(String::compareTo);
        dto.setFirstPurchaseDate(firstDate.orElse("N/A"));
        
        Optional<String> lastDate = validInvoices.stream()
                .map(Invoice::getInvoiceDate)
                .filter(Objects::nonNull)
                .max(String::compareTo);
        dto.setLastPurchaseDate(lastDate.orElse("N/A"));
        
        // Return statistics
        long returnedOrdersCount = returnedInvoices.stream()
                .map(Invoice::getInvoiceNo)
                .distinct()
                .count();
        dto.setReturnedOrders(returnedOrdersCount);
        
        double returnRate = totalOrders > 0 ? (returnedOrdersCount * 100.0 / totalOrders) : 0.0;
        dto.setReturnRate(returnRate);
        
        // Customer segment
        dto.setCustomerSegment(calculateCustomerSegment(totalRevenue, totalOrders));
        
        // Activity status
        dto.setDaysSinceLastPurchase(calculateDaysSinceLastPurchase(lastDate.orElse(null)));
        dto.setStatus(calculateCustomerStatus(dto.getDaysSinceLastPurchase()));
        
        // Top product
        setTopProduct(dto, validInvoices);
        
        return dto;
    }
    
    /**
     * Calculate customer segment based on revenue and order count
     */
    private String calculateCustomerSegment(double totalRevenue, long totalOrders) {
        if (totalRevenue > 10000 && totalOrders > 20) {
            return "VIP";
        } else if (totalRevenue > 5000 && totalOrders > 10) {
            return "Premium";
        } else if (totalRevenue > 1000 && totalOrders > 5) {
            return "Regular";
        } else if (totalOrders <= 2) {
            return "New";
        } else {
            return "Basic";
        }
    }
    
    /**
     * Calculate days since last purchase
     */
    private Integer calculateDaysSinceLastPurchase(String lastPurchaseDate) {
        if (lastPurchaseDate == null || lastPurchaseDate.equals("N/A")) {
            return null;
        }
        
        try {
            LocalDate lastDate = LocalDate.parse(lastPurchaseDate.substring(0, 10));
            LocalDate now = LocalDate.of(2011, 12, 9); // Dataset end date
            return (int) ChronoUnit.DAYS.between(lastDate, now);
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * Calculate customer status based on days since last purchase
     */
    private String calculateCustomerStatus(Integer daysSinceLastPurchase) {
        if (daysSinceLastPurchase == null) {
            return "Unknown";
        }
        
        if (daysSinceLastPurchase <= 30) {
            return "Active";
        } else if (daysSinceLastPurchase <= 90) {
            return "At-Risk";
        } else if (daysSinceLastPurchase <= 180) {
            return "Inactive";
        } else {
            return "Churned";
        }
    }
    
    /**
     * Set top purchased product for customer
     */
    private void setTopProduct(CustomerDTO dto, List<Invoice> validInvoices) {
        Map<String, Long> productQuantities = validInvoices.stream()
                .filter(inv -> inv.getStockCode() != null && inv.getQuantity() != null)
                .collect(Collectors.groupingBy(
                        Invoice::getStockCode,
                        Collectors.summingLong(inv -> inv.getQuantity())
                ));
        
        if (!productQuantities.isEmpty()) {
            Map.Entry<String, Long> topEntry = productQuantities.entrySet().stream()
                    .max(Map.Entry.comparingByValue())
                    .orElse(null);
            
            if (topEntry != null) {
                dto.setTopProductStockCode(topEntry.getKey());
                dto.setTopProductQuantity(topEntry.getValue());
                
                // Get description
                validInvoices.stream()
                        .filter(inv -> topEntry.getKey().equals(inv.getStockCode()))
                        .map(Invoice::getDescription)
                        .filter(Objects::nonNull)
                        .findFirst()
                        .ifPresent(dto::setTopProductDescription);
            }
        }
    }
}
