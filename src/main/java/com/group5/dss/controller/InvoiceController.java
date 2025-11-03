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
            Model model) {
        
        Page<Invoice> invoicePage = invoiceService.getAllInvoices(page, size);
        
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

