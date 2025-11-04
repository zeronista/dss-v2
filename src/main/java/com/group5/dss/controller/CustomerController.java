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
            Model model) {
        
        List<CustomerDTO> customers;
        
        if (search != null && !search.trim().isEmpty()) {
            customers = customerService.searchCustomers(search);
            model.addAttribute("searchQuery", search);
        } else {
            customers = customerService.getAllCustomers();
        }
        
        // Calculate summary statistics
        long totalCustomers = customers.size();
        
        double totalRevenue = customers.stream()
                .mapToDouble(CustomerDTO::getTotalRevenue)
                .sum();
        
        double averageRevenue = totalCustomers > 0 ? totalRevenue / totalCustomers : 0.0;
        
        long vipCustomers = customers.stream()
                .filter(c -> "VIP".equals(c.getCustomerSegment()))
                .count();
        
        long activeCustomers = customers.stream()
                .filter(c -> "Active".equals(c.getStatus()))
                .count();
        
        model.addAttribute("customers", customers);
        model.addAttribute("totalCustomers", totalCustomers);
        model.addAttribute("totalRevenue", totalRevenue);
        model.addAttribute("averageRevenue", averageRevenue);
        model.addAttribute("vipCustomers", vipCustomers);
        model.addAttribute("activeCustomers", activeCustomers);
        
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
