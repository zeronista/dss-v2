package com.group5.dss.service;

import com.group5.dss.model.Role;
import com.group5.dss.model.User;
import com.group5.dss.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    public User createUser(String username, String password, String fullName, String email, Role role) {
        if (userRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists");
        }
        
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setFullName(fullName);
        user.setEmail(email);
        user.setRole(role);
        user.setEnabled(true);
        
        return userRepository.save(user);
    }
    
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }
    
    public Optional<User> findById(String id) {
        return userRepository.findById(id);
    }
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public void initializeDefaultUsers() {
        if (userRepository.count() == 0) {
            // Create default users for each role
            createUser("admin", "admin123", "Admin User", "admin@dss.com", Role.ADMIN);
            createUser("inventory", "inventory123", "Inventory Manager", "inventory@dss.com", Role.INVENTORY_MANAGER);
            createUser("marketing", "marketing123", "Marketing Manager", "marketing@dss.com", Role.MARKETING_MANAGER);
            createUser("sales", "sales123", "Sales Manager", "sales@dss.com", Role.SALES_MANAGER);
        }
    }
}

