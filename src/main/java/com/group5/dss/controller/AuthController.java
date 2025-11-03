package com.group5.dss.controller;

import com.group5.dss.model.User;
import com.group5.dss.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Collection;

@Controller
public class AuthController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/login")
    public String login(Model model) {
        return "login";
    }
    
    @GetMapping("/dashboard")
    public String dashboard(Model model) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        
        User user = userService.findByUsername(username).orElse(null);
        model.addAttribute("user", user);
        
        // Redirect based on role
        Collection<? extends GrantedAuthority> authorities = auth.getAuthorities();
        
        for (GrantedAuthority authority : authorities) {
            String role = authority.getAuthority();
            
            switch (role) {
                case "ROLE_ADMIN":
                    return "redirect:/admin/dashboard";
                case "ROLE_INVENTORY_MANAGER":
                    return "redirect:/inventory/dashboard";
                case "ROLE_MARKETING_MANAGER":
                    return "redirect:/marketing/dashboard";
                case "ROLE_SALES_MANAGER":
                    return "redirect:/sales/dashboard";
            }
        }
        
        return "redirect:/login";
    }
    
    @GetMapping("/admin/dashboard")
    public String adminDashboard(Model model) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        User user = userService.findByUsername(username).orElse(null);
        model.addAttribute("user", user);
        return "dashboard/admin";
    }
    
    @GetMapping("/inventory/dashboard")
    public String inventoryDashboard(Model model) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        User user = userService.findByUsername(username).orElse(null);
        model.addAttribute("user", user);
        return "dashboard/inventory";
    }
    
    @GetMapping("/marketing/dashboard")
    public String marketingDashboard(Model model) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        User user = userService.findByUsername(username).orElse(null);
        model.addAttribute("user", user);
        return "dashboard/marketing";
    }
    
    @GetMapping("/sales/dashboard")
    public String salesDashboard(Model model) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        User user = userService.findByUsername(username).orElse(null);
        model.addAttribute("user", user);
        return "dashboard/sales";
    }
}

