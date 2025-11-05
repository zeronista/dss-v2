package com.group5.dss.service;

import com.group5.dss.model.Invoice;
import com.group5.dss.util.LocalDataLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class InvoiceService {
    
    @Autowired
    private LocalDataLoader localDataLoader;
    
    /**
     * Get all invoices with pagination from FULL LOCAL CSV
     * Using FULL dataset including cancelled orders for Admin role
     */
    public Page<Invoice> getAllInvoices(int page, int size) {
        System.out.println("📋 Loading invoices from FULL LOCAL CSV (including cancelled orders)...");
        
        // Load all invoices from local CSV (FULL dataset)
        List<Invoice> allInvoices = localDataLoader.loadFullTransactions();
        
        // Implement pagination manually
        int totalElements = allInvoices.size();
        int startIndex = page * size;
        int endIndex = Math.min(startIndex + size, totalElements);
        
        // Get invoices for current page
        List<Invoice> pageContent = (startIndex < totalElements) 
            ? new ArrayList<>(allInvoices.subList(startIndex, endIndex))
            : new ArrayList<>();
        
        // Create Page object
        Pageable pageable = PageRequest.of(page, size);
        Page<Invoice> invoicePage = new PageImpl<>(pageContent, pageable, totalElements);
        
        System.out.println("✅ Loaded page " + (page + 1) + " with " + pageContent.size() + " invoices (Total: " + totalElements + ")");
        
        return invoicePage;
    }
    
    /**
     * Get total count of invoices from FULL LOCAL CSV
     */
    public long getTotalCount() {
        List<Invoice> allInvoices = localDataLoader.loadFullTransactions();
        return allInvoices.size();
    }
}

