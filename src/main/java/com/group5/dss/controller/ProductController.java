package com.group5.dss.controller;

import com.group5.dss.model.ProductDTO;
import com.group5.dss.service.ProductService;
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
public class ProductController {
    
    @Autowired
    private ProductService productService;
    
    @GetMapping("/products")
    public String listProducts(
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Model model) {
        
        List<ProductDTO> allProducts;
        
        if (search != null && !search.trim().isEmpty()) {
            allProducts = productService.searchProducts(search);
            model.addAttribute("searchQuery", search);
        } else {
            allProducts = productService.getAllProducts();
        }
        
        // Calculate totals from all products
        double totalRevenue = allProducts.stream()
                .mapToDouble(ProductDTO::getTotalRevenue)
                .sum();
        
        long totalQuantity = allProducts.stream()
                .mapToLong(ProductDTO::getTotalQuantitySold)
                .sum();
        
        // Pagination logic
        int totalProducts = allProducts.size();
        int totalPages = (int) Math.ceil((double) totalProducts / size);
        
        // Ensure page is within bounds
        if (page < 1) page = 1;
        if (page > totalPages && totalPages > 0) page = totalPages;
        
        // Get products for current page
        int startIndex = (page - 1) * size;
        int endIndex = Math.min(startIndex + size, totalProducts);
        List<ProductDTO> products = allProducts.subList(startIndex, endIndex);
        
        model.addAttribute("products", products);
        model.addAttribute("totalProducts", totalProducts);
        model.addAttribute("totalRevenue", totalRevenue);
        model.addAttribute("totalQuantity", totalQuantity);
        model.addAttribute("currentPage", page);
        model.addAttribute("pageSize", size);
        model.addAttribute("totalPages", totalPages);
        
        return "admin/products";
    }
    
    @GetMapping("/products/{stockCode}")
    public String productDetails(@PathVariable String stockCode, Model model) {
        ProductDTO product = productService.getProductByStockCode(stockCode)
                .orElseThrow(() -> new RuntimeException("Product not found with stock code: " + stockCode));
        
        model.addAttribute("product", product);
        return "admin/product-details";
    }
}
