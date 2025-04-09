import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class FoodRecommendationModel(nn.Module):
    """
    PyTorch neural network model for food recommendation
    
    This model creates embeddings for user profiles and food items
    to enable similarity-based recommendations.
    """
    
    def __init__(self, input_size, hidden_size, output_size):
        """
        Initialize the model
        
        Args:
            input_size (int): Size of input features
            hidden_size (int): Size of hidden layer
            output_size (int): Size of output embedding
        """
        super(FoodRecommendationModel, self).__init__()
        
        # Define model layers
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, output_size),
            nn.Tanh()  # Output embedding in range [-1, 1]
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Output embedding
        """
        # Ensure input is the right size
        if isinstance(x, list):
            x = torch.FloatTensor(x)
        
        # If input is one-dimensional, add batch dimension
        if len(x.shape) == 1:
            x = x.unsqueeze(0)
        
        # Pad or truncate input to match expected input_size
        expected_size = self.network[0].in_features
        actual_size = x.shape[1]
        
        if actual_size < expected_size:
            # Pad with zeros
            padding = torch.zeros(x.shape[0], expected_size - actual_size)
            x = torch.cat([x, padding], dim=1)
        elif actual_size > expected_size:
            # Truncate
            x = x[:, :expected_size]
        
        return self.network(x).squeeze(0)

def train_model(model, user_features, food_features, user_food_ratings, epochs=100, lr=0.001):
    """
    Train the recommendation model
    
    Args:
        model (FoodRecommendationModel): The model to train
        user_features (torch.Tensor): User profile features
        food_features (torch.Tensor): Food item features
        user_food_ratings (torch.Tensor): User-food ratings matrix
        epochs (int): Number of training epochs
        lr (float): Learning rate
        
    Returns:
        FoodRecommendationModel: Trained model
    """
    # Set up optimizer
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Define loss function
    criterion = nn.MSELoss()
    
    # Training loop
    for epoch in range(epochs):
        total_loss = 0
        
        for user_idx in range(len(user_features)):
            # Get user embedding
            user_embedding = model(user_features[user_idx])
            
            for food_idx in range(len(food_features)):
                # Skip if rating is missing
                if torch.isnan(user_food_ratings[user_idx, food_idx]):
                    continue
                
                # Get food embedding
                food_embedding = model(food_features[food_idx])
                
                # Calculate predicted rating (similarity)
                pred_rating = torch.nn.functional.cosine_similarity(
                    user_embedding.unsqueeze(0), 
                    food_embedding.unsqueeze(0)
                )
                
                # Calculate loss
                loss = criterion(pred_rating, user_food_ratings[user_idx, food_idx].unsqueeze(0))
                
                # Backward pass and optimization
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
        
        # Print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")
    
    return model

def recommend_foods(model, user_features, food_features, food_indices, top_n=10):
    """
    Recommend foods for a user
    
    Args:
        model (FoodRecommendationModel): Trained model
        user_features (torch.Tensor): User profile features
        food_features (torch.Tensor): Food item features
        food_indices (list): Indices of food items
        top_n (int): Number of recommendations to return
        
    Returns:
        list: Top food indices
    """
    # Set model to evaluation mode
    model.eval()
    
    with torch.no_grad():
        # Get user embedding
        user_embedding = model(user_features)
        
        # Calculate similarity with all foods
        similarities = []
        
        for idx, food_feature in enumerate(food_features):
            food_embedding = model(food_feature)
            similarity = torch.nn.functional.cosine_similarity(
                user_embedding.unsqueeze(0), 
                food_embedding.unsqueeze(0)
            )
            similarities.append((food_indices[idx], similarity.item()))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N recommendations
        return [idx for idx, _ in similarities[:top_n]]
