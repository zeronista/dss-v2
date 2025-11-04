package com.group5.dss.util;

import com.group5.dss.model.Invoice;
import org.springframework.stereotype.Component;

import java.io.*;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Utility class to load transaction data from local CSV file
 * Similar to Python APIs approach - uses local file for better performance
 */
@Component
public class LocalDataLoader {
    
    private static final String DATA_DIR = "data";
    private static final String CLEANED_CSV = "online_retail_cleaned.csv";
    private static final String FULL_CSV = "online_retail.csv";
    
    // Cache
    private static List<Invoice> cachedCleanedData = null;
    private static List<Invoice> cachedFullData = null;
    private static LocalDateTime cacheTimestamp = null;
    private static final int CACHE_TTL_SECONDS = 3600; // 1 hour
    
    /**
     * Load cleaned transactions from local CSV file (for Products, Customers, Sales, Marketing, Admin)
     */
    public List<Invoice> loadCleanedTransactions() {
        return loadTransactions(CLEANED_CSV, false);
    }
    
    /**
     * Load FULL transactions including returns/cancellations (for Inventory Manager)
     */
    public List<Invoice> loadFullTransactions() {
        return loadTransactions(FULL_CSV, true);
    }
    
    /**
     * Load transactions from specified CSV file with caching
     */
    private List<Invoice> loadTransactions(String filename, boolean includeCancelled) {
        // Check cache validity
        if (cacheTimestamp != null && 
            LocalDateTime.now().minusSeconds(CACHE_TTL_SECONDS).isBefore(cacheTimestamp)) {
            
            List<Invoice> cachedData = includeCancelled ? cachedFullData : cachedCleanedData;
            if (cachedData != null) {
                System.out.println("✅ Using cached data (" + cachedData.size() + " rows)");
                return new ArrayList<>(cachedData); // Return copy
            }
        }
        
        System.out.println("📂 Loading data from local CSV: " + filename);
        
        List<Invoice> invoices = new ArrayList<>();
        String filePath = findDataFile(filename);
        
        if (filePath == null) {
            System.err.println("❌ Data file not found: " + filename);
            return invoices;
        }
        
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            String[] headers = null;
            int lineNumber = 0;
            
            while ((line = br.readLine()) != null) {
                lineNumber++;
                
                // Parse headers
                if (lineNumber == 1) {
                    headers = parseCsvLine(line);
                    continue;
                }
                
                try {
                    Invoice invoice = parseCsvLineToInvoice(line, headers);
                    if (invoice != null) {
                        invoices.add(invoice);
                    }
                } catch (Exception e) {
                    // Skip malformed lines
                    if (lineNumber % 10000 == 0) {
                        System.out.println("⚠️  Skipped malformed line " + lineNumber);
                    }
                }
            }
            
            System.out.println("✅ Loaded " + invoices.size() + " transactions from " + filename);
            
            // Update cache
            if (includeCancelled) {
                cachedFullData = new ArrayList<>(invoices);
            } else {
                cachedCleanedData = new ArrayList<>(invoices);
            }
            cacheTimestamp = LocalDateTime.now();
            
        } catch (IOException e) {
            System.err.println("❌ Error reading CSV file: " + e.getMessage());
        }
        
        return invoices;
    }
    
    /**
     * Find data file in project directory
     */
    private String findDataFile(String filename) {
        // Try multiple possible locations
        String[] possiblePaths = {
            DATA_DIR + File.separator + filename,
            ".." + File.separator + DATA_DIR + File.separator + filename,
            "." + File.separator + DATA_DIR + File.separator + filename,
            filename
        };
        
        for (String path : possiblePaths) {
            File file = new File(path);
            if (file.exists()) {
                System.out.println("📁 Found data file at: " + file.getAbsolutePath());
                return file.getAbsolutePath();
            }
        }
        
        return null;
    }
    
    /**
     * Parse CSV line considering quoted fields
     */
    private String[] parseCsvLine(String line) {
        List<String> fields = new ArrayList<>();
        StringBuilder currentField = new StringBuilder();
        boolean inQuotes = false;
        
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.add(currentField.toString().trim());
                currentField = new StringBuilder();
            } else {
                currentField.append(c);
            }
        }
        
        fields.add(currentField.toString().trim());
        return fields.toArray(new String[0]);
    }
    
    /**
     * Parse CSV line to Invoice object
     */
    private Invoice parseCsvLineToInvoice(String line, String[] headers) {
        String[] fields = parseCsvLine(line);
        
        if (fields.length < headers.length) {
            return null; // Skip incomplete rows
        }
        
        Invoice invoice = new Invoice();
        
        for (int i = 0; i < headers.length && i < fields.length; i++) {
            String header = headers[i].trim();
            String value = fields[i].trim();
            
            if (value.isEmpty() || value.equalsIgnoreCase("null")) {
                continue;
            }
            
            try {
                switch (header) {
                    case "InvoiceNo":
                        invoice.setInvoiceNo(parseLong(value));
                        break;
                    case "StockCode":
                        invoice.setStockCode(value);
                        break;
                    case "Description":
                        invoice.setDescription(value);
                        break;
                    case "Quantity":
                        invoice.setQuantity(parseInt(value));
                        break;
                    case "InvoiceDate":
                        invoice.setInvoiceDate(value);
                        break;
                    case "UnitPrice":
                        invoice.setUnitPrice(parseDouble(value));
                        break;
                    case "CustomerID":
                        invoice.setCustomerId(parseInt(value));
                        break;
                    case "Country":
                        invoice.setCountry(value);
                        break;
                    case "TotalPrice":
                    case "Revenue":
                        invoice.setTotalPrice(parseDouble(value));
                        break;
                    case "InvoiceYear":
                        invoice.setInvoiceYear(parseInt(value));
                        break;
                    case "InvoiceMonth":
                        invoice.setInvoiceMonth(parseInt(value));
                        break;
                }
            } catch (Exception e) {
                // Skip invalid values
            }
        }
        
        // Calculate TotalPrice if not provided
        if (invoice.getTotalPrice() == null && 
            invoice.getQuantity() != null && 
            invoice.getUnitPrice() != null) {
            invoice.setTotalPrice(invoice.getQuantity() * invoice.getUnitPrice());
        }
        
        return invoice;
    }
    
    private Integer parseInt(String value) {
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return null;
        }
    }
    
    private Long parseLong(String value) {
        try {
            // Remove any non-numeric characters except minus sign
            value = value.replaceAll("[^0-9-]", "");
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            return null;
        }
    }
    
    private Double parseDouble(String value) {
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException e) {
            return null;
        }
    }
    
    /**
     * Clear cache - useful for testing or forcing reload
     */
    public void clearCache() {
        cachedCleanedData = null;
        cachedFullData = null;
        cacheTimestamp = null;
        System.out.println("🗑️  Cache cleared");
    }
}
