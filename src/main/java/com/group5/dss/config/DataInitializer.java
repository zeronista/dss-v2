package com.group5.dss.config;

import com.group5.dss.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {
    
    @Autowired
    private UserService userService;
    
    @Override
    public void run(String... args) throws Exception {
        // Initialize default users if database is empty
        userService.initializeDefaultUsers();
        System.out.println("✅ Default users initialized successfully!");
    }
}

