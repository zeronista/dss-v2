package com.group5.dss.controller;

import com.group5.dss.model.OrderDTO;
import com.group5.dss.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@Controller
@RequestMapping("/admin")
@PreAuthorize("hasRole('ADMIN')")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @GetMapping("/orders")
    public String listOrders(
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Model model) {
        
        List<OrderDTO> allOrders;
        
        if (search != null && !search.trim().isEmpty()) {
            allOrders = orderService.searchOrders(search);
            model.addAttribute("searchQuery", search);
        } else {
            allOrders = orderService.getAllOrders();
        }
        
        // Calculate totals from all orders
        long totalOrders = allOrders.size();
        
        double totalRevenue = allOrders.stream()
                .mapToDouble(OrderDTO::getTotalAmount)
                .sum();
        
        long totalItems = allOrders.stream()
                .mapToLong(OrderDTO::getTotalItems)
                .sum();
        
        long completedOrders = allOrders.stream()
                .filter(o -> "Completed".equals(o.getStatus()))
                .count();
        
        long cancelledOrders = allOrders.stream()
                .filter(o -> "Cancelled".equals(o.getStatus()))
                .count();
        
        // Pagination logic
        int totalPages = (int) Math.ceil((double) totalOrders / size);
        
        // Ensure page is within bounds
        if (page < 1) page = 1;
        if (page > totalPages && totalPages > 0) page = totalPages;
        
        // Get orders for current page
        int startIndex = (page - 1) * size;
        int endIndex = Math.min(startIndex + size, (int) totalOrders);
        List<OrderDTO> orders = allOrders.subList(startIndex, endIndex);
        
        model.addAttribute("orders", orders);
        model.addAttribute("totalOrders", totalOrders);
        model.addAttribute("totalRevenue", totalRevenue);
        model.addAttribute("totalItems", totalItems);
        model.addAttribute("completedOrders", completedOrders);
        model.addAttribute("cancelledOrders", cancelledOrders);
        model.addAttribute("currentPage", page);
        model.addAttribute("pageSize", size);
        model.addAttribute("totalPages", totalPages);
        
        return "admin/orders";
    }
    
    @GetMapping("/orders/{invoiceNo}")
    public String orderDetails(@PathVariable Long invoiceNo, Model model) {
        OrderDTO order = orderService.getOrderByInvoiceNo(invoiceNo)
                .orElseThrow(() -> new RuntimeException("Order not found with invoice number: " + invoiceNo));
        
        model.addAttribute("order", order);
        return "admin/order-details";
    }
}
