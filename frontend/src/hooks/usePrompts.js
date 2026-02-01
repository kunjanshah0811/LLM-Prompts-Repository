import { useState, useEffect } from 'react';
import { promptsAPI } from '../utils/api';

export const usePrompts = (filters = {}) => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setLoading(true);
        const data = await promptsAPI.getPrompts(filters);
        setPrompts(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching prompts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrompts();
  }, [JSON.stringify(filters)]);

  return { prompts, loading, error, setPrompts };
};

export const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await promptsAPI.getCategories();
        setCategories(data.categories);
      } catch (err) {
        console.error('Error fetching categories:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, loading };
};
