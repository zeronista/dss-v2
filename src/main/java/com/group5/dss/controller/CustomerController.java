package com.group5.dss.controller;

import com.group5.dss.model.CustomerDTO;
import com.group5.dss.service.CustomerService;
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
public class CustomerController {
    
    @Autowired
    private CustomerService customerService;
    
    @GetMapping("/customers")
    public String listCustomers(
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Model model) {
        
        List<CustomerDTO> allCustomers;
        
        if (search != null && !search.trim().isEmpty()) {
            allCustomers = customerService.searchCustomers(search);
            model.addAttribute("searchQuery", search);
        } else {
            allCustomers = customerService.getAllCustomers();
        }
        
        // Calculate summary statistics from all customers
        long totalCustomers = allCustomers.size();
        
        double totalRevenue = allCustomers.stream()
                .mapToDouble(CustomerDTO::getTotalRevenue)
                .sum();
        
        double averageRevenue = totalCustomers > 0 ? totalRevenue / totalCustomers : 0.0;
        
        long vipCustomers = allCustomers.stream()
                .filter(c -> "VIP".equals(c.getCustomerSegment()))
                .count();
        
        long activeCustomers = allCustomers.stream()
                .filter(c -> "Active".equals(c.getStatus()))
                .count();
        
        // Pagination logic
        int totalPages = (int) Math.ceil((double) totalCustomers / size);
        
        // Ensure page is within bounds
        if (page < 1) page = 1;
        if (page > totalPages && totalPages > 0) page = totalPages;
        
        // Get customers for current page
        int startIndex = (page - 1) * size;
        int endIndex = Math.min(startIndex + size, (int) totalCustomers);
        List<CustomerDTO> customers = allCustomers.subList(startIndex, endIndex);
        
        model.addAttribute("customers", customers);
        model.addAttribute("totalCustomers", totalCustomers);
        model.addAttribute("totalRevenue", totalRevenue);
        model.addAttribute("averageRevenue", averageRevenue);
        model.addAttribute("vipCustomers", vipCustomers);
        model.addAttribute("activeCustomers", activeCustomers);
        model.addAttribute("currentPage", page);
        model.addAttribute("pageSize", size);
        model.addAttribute("totalPages", totalPages);
        
        return "admin/customers";
    }
    
    @GetMapping("/customers/{id}")
    public String customerDetails(@PathVariable Integer id, Model model) {
        CustomerDTO customer = customerService.getCustomerById(id)
                .orElseThrow(() -> new RuntimeException("Customer not found with id: " + id));
        
        model.addAttribute("customer", customer);
        return "admin/customer-details";
    }
}
