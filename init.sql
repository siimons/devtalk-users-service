CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,             
    article_id INT NOT NULL,          
    content TEXT NOT NULL,              
    created_at DATETIME DEFAULT NOW(),  
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_article FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);
