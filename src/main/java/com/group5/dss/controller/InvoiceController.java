package com.group5.dss.controller;

import com.group5.dss.model.Invoice;
import com.group5.dss.service.InvoiceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class InvoiceController {
    
    @Autowired
    private InvoiceService invoiceService;
    
    @GetMapping("/")
    public String home() {
        return "redirect:/invoices";
    }
    
    @GetMapping("/invoices")
    public String getInvoices(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "25") int size,
            @RequestParam(required = false) String invoiceNo,
            @RequestParam(required = false) String stockCode,
            @RequestParam(required = false) String description,
            @RequestParam(required = false) String customerId,
            @RequestParam(required = false) String country,
            Model model) {
        
        Page<Invoice> invoicePage;
        
        // Check if any search parameter is provided
        boolean hasSearchParams = (invoiceNo != null && !invoiceNo.trim().isEmpty()) ||
                                 (stockCode != null && !stockCode.trim().isEmpty()) ||
                                 (description != null && !description.trim().isEmpty()) ||
                                 (customerId != null && !customerId.trim().isEmpty()) ||
                                 (country != null && !country.trim().isEmpty());
        
        if (hasSearchParams) {
            // Search with filters
            invoicePage = invoiceService.searchInvoices(
                invoiceNo, 
                stockCode, 
                description, 
                customerId, 
                country, 
                page, 
                size
            );
        } else {
            // Get all invoices
            invoicePage = invoiceService.getAllInvoices(page, size);
        }
        
        model.addAttribute("invoices", invoicePage.getContent());
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", invoicePage.getTotalPages());
        model.addAttribute("totalItems", invoicePage.getTotalElements());
        model.addAttribute("pageSize", size);
        model.addAttribute("hasNext", invoicePage.hasNext());
        model.addAttribute("hasPrevious", invoicePage.hasPrevious());
        
        return "invoices";
    }
}

