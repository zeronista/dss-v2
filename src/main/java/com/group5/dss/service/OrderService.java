package com.group5.dss.service;

import com.group5.dss.model.Invoice;
import com.group5.dss.model.OrderDTO;
import com.group5.dss.util.LocalDataLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class OrderService {
    
    @Autowired
    private LocalDataLoader localDataLoader;
    
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("M/d/yyyy H:mm");
    
    /**
     * Get all orders aggregated from LOCAL CSV file
     */
    public List<OrderDTO> getAllOrders() {
        System.out.println("📋 Loading orders from LOCAL CSV...");
        List<Invoice> invoices = localDataLoader.loadCleanedTransactions();
        
        // Group invoices by InvoiceNo
        Map<Long, List<Invoice>> groupedByInvoice = invoices.stream()
                .filter(inv -> inv.getInvoiceNo() != null)
                .collect(Collectors.groupingBy(Invoice::getInvoiceNo));
        
        // Build order DTOs
        List<OrderDTO> orders = new ArrayList<>();
        
        for (Map.Entry<Long, List<Invoice>> entry : groupedByInvoice.entrySet()) {
            Long invoiceNo = entry.getKey();
            List<Invoice> orderInvoices = entry.getValue();
            
            OrderDTO order = buildOrderDTO(invoiceNo, orderInvoices);
            orders.add(order);
        }
        
        // Sort by invoice date (newest first)
        orders.sort((o1, o2) -> {
            try {
                LocalDateTime date1 = LocalDateTime.parse(o1.getInvoiceDate(), DATE_FORMATTER);
                LocalDateTime date2 = LocalDateTime.parse(o2.getInvoiceDate(), DATE_FORMATTER);
                return date2.compareTo(date1);
            } catch (Exception e) {
                return o2.getInvoiceNo().compareTo(o1.getInvoiceNo());
            }
        });
        
        System.out.println("✅ Loaded " + orders.size() + " orders from LOCAL CSV");
        return orders;
    }
    
    /**
     * Get order by invoice number
     */
    public Optional<OrderDTO> getOrderByInvoiceNo(Long invoiceNo) {
        System.out.println("🔍 Finding order: " + invoiceNo);
        List<Invoice> invoices = localDataLoader.loadCleanedTransactions();
        
        List<Invoice> orderInvoices = invoices.stream()
                .filter(inv -> invoiceNo.equals(inv.getInvoiceNo()))
                .collect(Collectors.toList());
        
        if (orderInvoices.isEmpty()) {
            return Optional.empty();
        }
        
        return Optional.of(buildOrderDTO(invoiceNo, orderInvoices));
    }
    
    /**
     * Search orders by invoice number, customer ID, or country
     */
    public List<OrderDTO> searchOrders(String query) {
        System.out.println("🔍 Searching orders for: " + query);
        List<OrderDTO> allOrders = getAllOrders();
        
        String searchLower = query.toLowerCase().trim();
        
        return allOrders.stream()
                .filter(order -> 
                    order.getInvoiceNo().toString().contains(searchLower) ||
                    (order.getCustomerId() != null && order.getCustomerId().toString().contains(searchLower)) ||
                    (order.getCountry() != null && order.getCountry().toLowerCase().contains(searchLower))
                )
                .collect(Collectors.toList());
    }
    
    /**
     * Build OrderDTO from list of invoices with same invoice number
     */
    private OrderDTO buildOrderDTO(Long invoiceNo, List<Invoice> invoices) {
        OrderDTO order = new OrderDTO();
        
        if (invoices.isEmpty()) {
            return order;
        }
        
        // Get first invoice for common information
        Invoice firstInvoice = invoices.get(0);
        
        // Set order identification
        order.setInvoiceNo(invoiceNo);
        order.setInvoiceDate(firstInvoice.getInvoiceDate());
        order.setInvoiceYear(firstInvoice.getInvoiceYear());
        order.setInvoiceMonth(firstInvoice.getInvoiceMonth());
        
        // Set customer information
        order.setCustomerId(firstInvoice.getCustomerId());
        order.setCountry(firstInvoice.getCountry());
        
        // Calculate order statistics
        int totalItems = 0;
        double totalAmount = 0.0;
        boolean hasCancellation = false;
        Set<String> uniqueProducts = new HashSet<>();
        
        List<OrderDTO.OrderItemDTO> items = new ArrayList<>();
        
        for (Invoice invoice : invoices) {
            // Check for cancellation (negative quantity)
            boolean isCancelled = invoice.getQuantity() != null && invoice.getQuantity() < 0;
            if (isCancelled) {
                hasCancellation = true;
            }
            
            // Calculate totals
            int qty = invoice.getQuantity() != null ? Math.abs(invoice.getQuantity()) : 0;
            double price = invoice.getTotalPrice() != null ? invoice.getTotalPrice() : 0.0;
            
            totalItems += qty;
            totalAmount += price;
            
            if (invoice.getStockCode() != null) {
                uniqueProducts.add(invoice.getStockCode());
            }
            
            // Create order item
            OrderDTO.OrderItemDTO item = new OrderDTO.OrderItemDTO();
            item.setStockCode(invoice.getStockCode());
            item.setDescription(invoice.getDescription());
            item.setQuantity(invoice.getQuantity());
            item.setUnitPrice(invoice.getUnitPrice());
            item.setTotalPrice(invoice.getTotalPrice());
            item.setIsCancelled(isCancelled);
            
            items.add(item);
        }
        
        order.setTotalItems(totalItems);
        order.setUniqueProducts(uniqueProducts.size());
        order.setTotalAmount(totalAmount);
        order.setIsCancelled(hasCancellation);
        order.setStatus(hasCancellation ? "Cancelled" : "Completed");
        order.setItems(items);
        
        // Parse date for additional information
        try {
            LocalDateTime dateTime = LocalDateTime.parse(firstInvoice.getInvoiceDate(), DATE_FORMATTER);
            order.setDayOfWeek(dateTime.getDayOfWeek().toString());
            
            int hour = dateTime.getHour();
            if (hour >= 5 && hour < 12) {
                order.setTimeOfDay("Morning");
            } else if (hour >= 12 && hour < 17) {
                order.setTimeOfDay("Afternoon");
            } else if (hour >= 17 && hour < 21) {
                order.setTimeOfDay("Evening");
            } else {
                order.setTimeOfDay("Night");
            }
        } catch (Exception e) {
            order.setDayOfWeek("Unknown");
            order.setTimeOfDay("Unknown");
        }
        
        return order;
    }
}
