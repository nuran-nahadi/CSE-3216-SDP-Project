
import React, { useState, useEffect, useRef } from 'react';
import {
  Mic, MicOff, Plus, Calendar, DollarSign, Tag, CreditCard, Building2, FileText, Clock, Trash2, Pencil, X, Image as ImageIcon,
  ArrowUpRight, ArrowDownRight, Bot, MessageCircle
} from 'lucide-react';
import { Building, Edit, Trash } from 'lucide-react';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { eventBus } from '../../utils/eventBus';
import { EXPENSE_CREATED, EXPENSE_UPDATED, EXPENSE_DELETED } from '../../utils/eventTypes';
// ... existing code ...
function getMonthYear(date) {
    const d = typeof date === 'string' ? new Date(date) : date;
    return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}`;
  }
  function getMonthName(date) {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleString('default', { month: 'long', year: 'numeric' });
  }
  
  const Breathing = () => (
    <div className="flex justify-center items-center py-2">
      <div className="w-6 h-6 rounded-full bg-blue-400 animate-pulse" style={{
        boxShadow: '0 0 0 8px #4fd1c580, 0 0 0 16px #81e6d950'
      }} />
      <span className="ml-2 text-blue-700 font-medium">Listening...</span>
    </div>
  );
  
  const CopilotIcon = ({ size = 52 }) => (
    <span
      className="inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <Bot size={size - 10} className="text-gray-900" />
    </span>
  );
  
  const ChatbotPanel = ({ open, onClose, onParseText, onParseReceipt, onParseVoice }) => {
    const [messages, setMessages] = useState([
      { from: 'bot', text: 'Hello! How can I help you today?' }
    ]);
    const [input, setInput] = useState('');
    const [listening, setListening] = useState(false);
    const [imagePreview, setImagePreview] = useState(null);
    const [audioBlob, setAudioBlob] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const streamRef = useRef(null); // Add this ref to track the stream

    useEffect(() => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, [messages, listening]);

    const handleParseText = async (text) => {
      setMessages(prev => [...prev, { from: 'user', text }]);
      setInput('');
      if (onParseText) {
        setMessages(prev => [...prev, { from: 'bot', text: 'Parsing with AI...' }]);
        const result = await onParseText(text);
        setMessages(prev => {
          const prevMsgs = [...prev.slice(0, -1)];
          if (result.error) {
            return [...prevMsgs, { from: 'bot', text: result.error }];
          }
          // Interactive reply for expense creation
          if (result.data) {
            const exp = result.data;
            const summary = `✅ Expense added!

- **Amount:** ${exp.amount} ${exp.currency || ''}
- **Category:** ${exp.category || ''}
- **Description:** ${exp.description || ''}
- **Date:** ${exp.date ? new Date(exp.date).toLocaleDateString() : ''}
${exp.merchant ? `- **Merchant:** ${exp.merchant}\n` : ''}${exp.tags && exp.tags.length ? `- **Tags:** ${exp.tags.join(', ')}` : ''}`;
            return [...prevMsgs, { from: 'bot', text: summary }];
          }
          return [...prevMsgs, { from: 'bot', text: result.message || 'Expense created successfully from text.' }];
        });
      }
    };

    const handleParseReceipt = async (file) => {
      setMessages(prev => [...prev, { from: 'user', image: URL.createObjectURL(file) }]);
      setImagePreview(null);
      if (onParseReceipt) {
        setMessages(prev => [...prev, { from: 'bot', text: 'Parsing receipt with AI...' }]);
        const result = await onParseReceipt(file);
        setMessages(prev => [
          ...prev.slice(0, -1),
          result.error
            ? { from: 'bot', text: result.error }
            : { from: 'bot', text: result.message || 'Receipt parsed!', data: result.data }
        ]);
      }
    };

    const handleParseVoice = async (file) => {
      setMessages(prev => [...prev, { from: 'user', text: '[Voice message]', audio: URL.createObjectURL(file) }]);
      setAudioBlob(null);
      if (onParseVoice) {
        setMessages(prev => [...prev, { from: 'bot', text: 'Parsing voice with AI...' }]);
        const result = await onParseVoice(file);
        setMessages(prev => [
          ...prev.slice(0, -1),
          result.error
            ? { from: 'bot', text: result.error }
            : { from: 'bot', text: result.message || 'Voice parsed!', data: result.data }
        ]);
      }
    };

    const handleSend = () => {
      if (!input.trim() && !imagePreview) return;
      if (input.trim()) handleParseText(input.trim());
      if (imagePreview) handleParseReceipt(imagePreview);
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Enter') handleSend();
    };

    // Fixed voice handling function
    const handleVoice = async () => {
      try {
        if (isRecording) {
          // Stop recording
          console.log('Stopping recording...');
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
          }
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
          }
          setIsRecording(false);
          setListening(false);
          return;
        }

        // Start recording
        if (!navigator.mediaDevices || !window.MediaRecorder) {
          alert('Audio recording not supported in this browser');
          return;
        }

        console.log('Starting recording...');
        setIsRecording(true);
        setListening(true);
        setAudioBlob(null);

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        
        const mediaRecorder = new window.MediaRecorder(stream, {
          mimeType: window.MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
        });
        mediaRecorderRef.current = mediaRecorder;

        const chunks = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunks.push(e.data);
          }
        };

        mediaRecorder.onstop = () => {
          console.log('Recording stopped, processing audio...');
          try {
            const mimeType = mediaRecorder.mimeType || 'audio/webm';
            const blob = new Blob(chunks, { type: mimeType });
            
            if (blob.size > 0) {
              setAudioBlob(blob);
              console.log('Audio blob created:', blob);
            } else {
              console.error('Empty audio blob');
              alert('Recording failed - empty audio data');
            }
          } catch (err) {
            console.error('Error processing audio:', err);
            alert('Error processing audio recording');
          } finally {
            setListening(false);
            setIsRecording(false);
            if (streamRef.current) {
              streamRef.current.getTracks().forEach(track => track.stop());
              streamRef.current = null;
            }
          }
        };

        mediaRecorder.onerror = (e) => {
          console.error('MediaRecorder error:', e);
          alert('Recording error occurred');
          setListening(false);
          setIsRecording(false);
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
          }
        };

        mediaRecorder.start(1000); // Collect data every second
        
      } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Error accessing microphone. Please check permissions.');
        setListening(false);
        setIsRecording(false);
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      }
    };

    const handleSendVoice = async () => {
      if (!audioBlob) {
        alert('No audio recorded');
        return;
      }
      console.log('Sending voice message...');
      await handleParseVoice(audioBlob);
    };

    const handleImage = () => {
      if (fileInputRef.current) fileInputRef.current.click();
    };

    const handleImageChange = (e) => {
      const file = e.target.files?.[0];
      if (file) setImagePreview(file);
    };

    // Cleanup function when component unmounts or panel closes
    useEffect(() => {
      return () => {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
        }
      };
    }, []);

    // Reset states when panel closes
    useEffect(() => {
      if (!open) {
        setIsRecording(false);
        setListening(false);
        setAudioBlob(null);
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      }
    }, [open]);

    return (
      <div
        className="fixed top-0 right-0 h-full w-full sm:w-[520px] max-w-[90vw] bg-white shadow-2xl z-50 transition-transform duration-300"
        style={{
          transform: open ? 'translateX(0)' : 'translateX(110%)',
          minWidth: 320,
          maxWidth: 560,
          pointerEvents: open ? 'auto' : 'none'
        }}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between px-4 py-3 border-b bg-blue-600 text-white">
            <div className="flex items-center space-x-2">
              <CopilotIcon size={28} />
              <span className="font-semibold">Copilot</span>
            </div>
            <button
              className="text-white hover:text-gray-200 p-1"
              onClick={onClose}
              aria-label="Close chat"
            >
              <X />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto px-4 py-3 bg-gray-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-3 flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.image ? (
                  <img
                    src={typeof msg.image === 'string' ? msg.image : URL.createObjectURL(msg.image)}
                    alt="User upload"
                    className="rounded-lg max-w-[70%] border border-gray-200"
                    style={{ maxHeight: 160 }}
                  />
                ) : msg.audio ? (
                  <audio controls src={msg.audio} className="max-w-[70%]" />
                ) : (
                  <div
                    className={`rounded-lg px-3 py-2 text-sm max-w-[80%] ${
                      msg.from === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    {msg.text}
                  </div>
                )}
              </div>
            ))}
            
            {/* Recording indicator */}
            {isRecording && (
              <div className="flex items-center space-x-2 py-2">
                <div className="w-4 h-4 rounded-full bg-red-500 animate-pulse" />
                <span className="text-red-700 font-medium">Recording... Click mic to stop</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <div className="px-4 py-3 border-t bg-white">
            <div className="flex items-center space-x-2">
              <button
                className={`p-2 rounded-full transition-colors ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-blue-100 hover:bg-blue-200 text-blue-700'
                }`}
                onClick={handleVoice}
                title={isRecording ? "Stop recording" : "Start recording"}
              >
                {isRecording ? <MicOff /> : <Mic />}
              </button>
              
              <button
                className="p-2 rounded-full bg-green-100 hover:bg-green-200 text-green-700"
                onClick={handleImage}
                title="Send image"
                disabled={!!imagePreview}
              >
                <ImageIcon />
              </button>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleImageChange}
              />
              
              <input
                type="text"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type your message..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={listening || isRecording}
              />
              
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                onClick={handleSend}
                disabled={(!input.trim() && !imagePreview) || listening || isRecording}
              >
                Send
              </button>
            </div>
            
            {/* Preview sections */}
            {(imagePreview || audioBlob) && (
              <div className="flex items-center mt-2 space-x-2">
                {imagePreview && (
                  <div className="flex items-center space-x-2">
                    <img 
                      src={URL.createObjectURL(imagePreview)} 
                      alt="Preview" 
                      className="h-12 w-12 rounded border object-cover" 
                    />
                    <button
                      className="text-red-500 text-xs underline hover:text-red-700"
                      onClick={() => setImagePreview(null)}
                    >
                      Remove
                    </button>
                  </div>
                )}
                
                {audioBlob && (
                  <div className="flex items-center space-x-2">
                    <audio 
                      controls 
                      src={URL.createObjectURL(audioBlob)} 
                      className="h-8"
                      style={{ minWidth: '200px' }}
                    />
                    <button
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                      onClick={handleSendVoice}
                    >
                      Send Voice
                    </button>
                    <button
                      className="text-red-500 text-xs underline hover:text-red-700"
                      onClick={() => setAudioBlob(null)}
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
const ExpenseTracker = () => {
  
  const [activeTab, setActiveTab] = useState('recent'); // 'recent' or 'summary'
  
  const [expenses, setExpenses] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [editingExpense, setEditingExpense] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'Taka',
    category: 'food',
    subcategory: '',
    merchant: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    payment_method: 'cash',
    is_recurring: false,
    recurrence_rule: '',
    tags: []
  });
  const [chatOpen, setChatOpen] = useState(false);
  const [insights, setInsights] = useState(null);

  const categories = ['food', 'transportation', 'utilities', 'entertainment', 'shopping', 'healthcare', 'other'];
  const paymentMethods = ['cash', 'card', 'bank_transfer', 'mobile_payment'];
  const currencies = ['Taka', 'USD', 'EUR'];

  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = async () => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          const formattedExpenses = result.data.map(expense => ({
            id: expense.id,
            date: new Date(expense.date).toLocaleDateString(),
            description: expense.description || 'No description',
            amount: expense.amount || 0,
            category: expense.category || 'other',
            currency: expense.currency || 'Taka',
            subcategory: expense.subcategory || '',
            merchant: expense.merchant || '',
            payment_method: expense.payment_method || 'cash',
            is_recurring: expense.is_recurring || false,
            recurrence_rule: expense.recurrence_rule || '',
            tags: expense.tags || []
          }));
          setExpenses(formattedExpenses);
        }
      }
    } catch (error) {
      setExpenses([]);
    }
  };

  const aiParseText = async (text) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/ai/parse-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const result = await response.json();
      if (result.success && result.data) {
        return { data: result.data, message: result.message || 'Parsed successfully.' };
      }
      return { error: result.message || 'Failed to parse text.' };
    } catch (error) {
      return { error: 'Network error while parsing text.' };
    }
  };

  const aiParseReceipt = async (file) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${baseUrl}/expenses/ai/parse-receipt`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      if (result.success && result.data) {
        return { data: result.data, message: result.message || 'Receipt parsed.' };
      }
      return { error: result.message || 'Failed to parse receipt.' };
    } catch (error) {
      return { error: 'Network error while parsing receipt.' };
    }
  };

  const aiParseVoice = async (file) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${baseUrl}/expenses/ai/parse-voice`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      if (result.success && result.data) {
        return { data: result.data, message: result.message || 'Voice parsed.' };
      }
      return { error: result.message || 'Failed to parse voice.' };
    } catch (error) {
      return { error: 'Network error while parsing voice.' };
    }
  };

  const fetchInsights = async (days = 30) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/ai/insights?days=${days}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      if (result.success && result.data) {
        setInsights(result.data);
      } else {
        setInsights(null);
      }
    } catch (error) {
      setInsights(null);
    }
  };

  // --- CRUD: Add/Edit/Delete ---
  const handleEdit = async (expenseId) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/${expenseId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      let expenseData;
      if (response.ok) {
        const result = await response.json();
        expenseData = result.data;
      } else {
        expenseData = expenses.find(expense => expense.id === expenseId);
      }
      if (expenseData) {
        const dateStr = expenseData.date
          ? new Date(expenseData.date).toISOString().split('T')[0]
          : new Date().toISOString().split('T')[0];
        setFormData({
          amount: expenseData.amount?.toString() || '',
          currency: expenseData.currency || 'Taka',
          category: expenseData.category || 'food',
          subcategory: expenseData.subcategory || '',
          merchant: expenseData.merchant || '',
          description: expenseData.description || '',
          date: dateStr,
          payment_method: expenseData.payment_method || 'cash',
          is_recurring: expenseData.is_recurring || false,
          recurrence_rule: expenseData.recurrence_rule || '',
          tags: expenseData.tags || []
        });
        setEditingExpense(expenseData);
        setIsEditing(true);
        setIsFormVisible(true);
      } else {
        alert('Expense not found');
      }
    } catch (error) {
      alert('Error loading expense for editing');
    }
  };

  const handleDelete = async (expenseId) => {
    if (!window.confirm('Are you sure you want to delete this expense?')) return;
    setDeletingId(expenseId);
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/${expenseId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        setExpenses(prev => prev.filter(expense => expense.id !== expenseId));
        // Publish event so other components know
        eventBus.publish(EXPENSE_DELETED, { id: expenseId });
        alert('Expense deleted successfully!');
      } else {
        alert('Failed to delete expense. Please try again.');
      }
    } catch (error) {
      setExpenses(prev => prev.filter(expense => expense.id !== expenseId));
      // Publish event even in demo mode
      eventBus.publish(EXPENSE_DELETED, { id: expenseId });
      alert('Expense deleted successfully! (Demo mode)');
    } finally {
      setDeletingId(null);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    setFormData(prev => ({
      ...prev,
      tags
    }));
  };

  const handleSubmit = async () => {
    if (!formData.amount || !formData.category) {
      alert('Please fill in required fields (Amount and Category)');
      return;
    }
    setIsSubmitting(true);
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const requestBody = {
        ...formData,
        amount: parseFloat(formData.amount),
        date: new Date(formData.date).toISOString()
      };
      let response;
      if (isEditing && editingExpense) {
        response = await fetch(`${baseUrl}/expenses/${editingExpense.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });
      } else {
        response = await fetch(`${baseUrl}/expenses/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });
      }
      if (response.ok) {
        const result = await response.json();
        const expenseData = {
          id: result.data.id || Date.now(),
          date: new Date(result.data.date).toLocaleDateString(),
          description: result.data.description || 'No description',
          amount: result.data.amount,
          category: result.data.category,
          currency: result.data.currency,
          subcategory: result.data.subcategory,
          merchant: result.data.merchant,
          payment_method: result.data.payment_method,
          is_recurring: result.data.is_recurring,
          recurrence_rule: result.data.recurrence_rule,
          tags: result.data.tags
        };
        if (isEditing) {
          setExpenses(prev => prev.map(expense =>
            expense.id === editingExpense.id ? expenseData : expense
          ));
          // Publish event so other components know
          eventBus.publish(EXPENSE_UPDATED, expenseData);
          alert('Expense updated successfully!');
        } else {
          setExpenses(prev => [expenseData, ...prev]);
          // Publish event so other components know
          eventBus.publish(EXPENSE_CREATED, expenseData);
          alert('Expense added successfully!');
        }
        resetForm();
      } else {
        const errorData = await response.json();
        alert('Failed to save expense. Please try again.');
      }
    } catch (error) {
      alert('Network error, but expense added locally.');
      const expenseData = {
        id: isEditing ? editingExpense.id : Date.now(),
        date: new Date(formData.date).toLocaleDateString(),
        description: formData.description || 'No description',
        amount: parseFloat(formData.amount),
        category: formData.category,
        currency: formData.currency,
        subcategory: formData.subcategory,
        merchant: formData.merchant,
        payment_method: formData.payment_method,
        is_recurring: formData.is_recurring,
        recurrence_rule: formData.recurrence_rule,
        tags: formData.tags
      };
      if (isEditing) {
        setExpenses(prev => prev.map(expense =>
          expense.id === editingExpense.id ? expenseData : expense
        ));
        alert('Expense updated successfully! (Demo mode)');
      } else {
        setExpenses(prev => [expenseData, ...prev]);
        alert('Expense added successfully! (Demo mode)');
      }
      resetForm();
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      amount: '',
      currency: 'Taka',
      category: 'food',
      subcategory: '',
      merchant: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
      payment_method: 'cash',
      is_recurring: false,
      recurrence_rule: '',
      tags: []
    });
    setIsFormVisible(false);
    setIsEditing(false);
    setEditingExpense(null);
  };

  const getCurrencySymbol = (currency) => {
    switch (currency) {
      case 'Taka': return '৳';
      case 'USD': return '$';
      case 'EUR': return '€';
      default: return '৳';
    }
  };

  // Dashboard endpoints state
  const [totalSpend, setTotalSpend] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [categoryTrend, setCategoryTrend] = useState([]);
  const [spendTrend, setSpendTrend] = useState([]);
  const [topTransactions, setTopTransactions] = useState([]);
  const [dashboardError, setDashboardError] = useState(null);

  // --- Dashboard Endpoints Integration ---
  useEffect(() => {
    fetchTotalSpend();
    fetchCategoryBreakdown();
    fetchCategoryTrend();
    fetchSpendTrend();
    fetchTopTransactions();
    // eslint-disable-next-line
  }, []);

  // a. /expenses/dashboard/total-spend
  const fetchTotalSpend = async () => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/dashboard/total-spend`);
      const result = await response.json();
      if (result.success && result.data) {
        setTotalSpend(result.data);
      } else {
        setDashboardError(result.message || 'Failed to fetch total spend.');
      }
    } catch {
      setDashboardError('Network error while fetching total spend.');
    }
  };

  // b. /expenses/dashboard/category-breakdown
  const fetchCategoryBreakdown = async (period = 'current_month') => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/dashboard/category-breakdown?period=${period}`);
      const result = await response.json();
      if (result.success && result.data) {
        setCategoryBreakdown(result.data);
      } else {
        setDashboardError(result.message || 'Failed to fetch category breakdown.');
      }
    } catch {
      setDashboardError('Network error while fetching category breakdown.');
    }
  };

  // c. /expenses/dashboard/category-trend
  const fetchCategoryTrend = async (months = 6) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/dashboard/category-trend?months=${months}`);
      const result = await response.json();
      if (result.success && result.data) {
        setCategoryTrend(result.data);
      } else {
        setDashboardError(result.message || 'Failed to fetch category trend.');
      }
    } catch {
      setDashboardError('Network error while fetching category trend.');
    }
  };

  // d. /expenses/dashboard/spend-trend
  const fetchSpendTrend = async (period = 'monthly', days = 180) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/dashboard/spend-trend?period=${period}&days=${days}`);
      const result = await response.json();
      if (result.success && result.data) {
        setSpendTrend(result.data);
      } else {
        setDashboardError(result.message || 'Failed to fetch spend trend.');
      }
    } catch {
      setDashboardError('Network error while fetching spend trend.');
    }
  };

  // e. /expenses/dashboard/top-transactions
  const fetchTopTransactions = async (period = 'monthly', limit = 5) => {
    try {
      const baseUrl = process.env.VITE_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/expenses/dashboard/top-transactions?period=${period}&limit=${limit}`);
      const result = await response.json();
      if (result.success && result.data) {
        setTopTransactions(result.data);
      } else {
        setDashboardError(result.message || 'Failed to fetch top transactions.');
      }
    } catch {
      setDashboardError('Network error while fetching top transactions.');
    }
  };

  // ... (rest of your CRUD, chatbot, and UI logic as before) ...

  // Add the dashboard display section at the top of your main content:
  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Navbar */}
      <div className="bg-white shadow-sm border-b fixed top-0 left-100 w-full z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-white">Expense Tracker</h1>
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setIsEditing(false);
                  setEditingExpense(null);
                  setFormData({
                    amount: '',
                    currency: 'Taka',
                    category: 'food',
                    subcategory: '',
                    merchant: '',
                    description: '',
                    date: new Date().toISOString().split('T')[0],
                    payment_method: 'cash',
                    is_recurring: false,
                    recurrence_rule: '',
                    tags: []
                  });
                  setIsFormVisible(!isFormVisible);
                }}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Expense
              </button>
            </div>
          </div>
          {/* Tabs */}
          <div className="flex space-x-2 border-b border-gray-200">
            <button
              className={`px-4 py-2 font-medium focus:outline-none transition-colors ${activeTab === 'recent' ? 'border-b-2 border-blue-600 text-blue-700 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setActiveTab('recent')}
            >
              Recent Expenses
            </button>
            <button
              className={`px-4 py-2 font-medium focus:outline-none transition-colors ${activeTab === 'summary' ? 'border-b-2 border-blue-600 text-blue-700 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'}`}
              onClick={() => setActiveTab('summary')}
            >
              Summary
            </button>
          </div>
        </div>
      </div>
      <div className="max-w-6xl mx-auto px-2 sm:px-8 pt-36 pb-8 min-h-screen">
        <div className="w-full">
          {/* Show Add/Edit Form if visible */}
          {isFormVisible && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              {/* ...form code as before... */}
              <h2 className="text-xl font-semibold mb-6">
                {isEditing ? 'Edit Expense' : 'Add New Expense'}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* ...form fields as before... */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DollarSign className="w-4 h-4 inline mr-1" />
                    Amount *
                  </label>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                  <select
                    name="currency"
                    value={formData.currency}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {currencies.map(currency => (
                      <option key={currency} value={currency}>{currency}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Tag className="w-4 h-4 inline mr-1" />
                    Category *
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {categories.map(category => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Subcategory</label>
                  <input
                    type="text"
                    name="subcategory"
                    value={formData.subcategory}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Dining out, Groceries"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Building className="w-4 h-4 inline mr-1" />
                    Merchant
                  </label>
                  <input
                    type="text"
                    name="merchant"
                    value={formData.merchant}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Store or restaurant name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-4 h-4 inline mr-1" />
                    Date *
                  </label>
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <CreditCard className="w-4 h-4 inline mr-1" />
                    Payment Method
                  </label>
                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {paymentMethods.map(method => (
                      <option key={method} value={method}>
                        {method.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                  <input
                    type="text"
                    value={formData.tags.join(', ')}
                    onChange={handleTagsChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Comma-separated tags"
                  />
                </div>
                <div className="lg:col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <FileText className="w-4 h-4 inline mr-1" />
                    Description
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Brief description of the expense"
                  />
                </div>
                <div className="lg:col-span-3">
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="is_recurring"
                        checked={formData.is_recurring}
                        onChange={handleInputChange}
                        className="mr-2"
                      />
                      <Clock className="w-4 h-4 mr-1" />
                      Recurring Expense
                    </label>
                    {formData.is_recurring && (
                      <input
                        type="text"
                        name="recurrence_rule"
                        value={formData.recurrence_rule}
                        onChange={handleInputChange}
                        placeholder="e.g., monthly, weekly"
                        className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    )}
                  </div>
                </div>
                <div className="lg:col-span-3 flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setIsFormVisible(false);
                      setIsEditing(false);
                      setEditingExpense(null);
                    }}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? (isEditing ? 'Updating...' : 'Adding...') : (isEditing ? 'Update Expense' : 'Add Expense')}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content */}
          <div className="w-full">
            {activeTab === 'summary' && (
              <div className="mb-8 overflow-y-auto" style={{ maxHeight: '70vh' }}>
                <h2 className="text-2xl font-bold mb-3">Summary</h2>
                {dashboardError && (
                  <div className="text-red-600 mb-2">{dashboardError}</div>
                )}
                {/* Total Spend */}
                {totalSpend && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="text-lg font-semibold text-blue-700">Total Spend</div>
                      <div className="text-2xl font-bold text-blue-900">
                        ৳{totalSpend.current_month} <span className="text-base text-gray-500">this month</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Previous: ৳{totalSpend.previous_month}
                      </div>
                    </div>
                    <div>
                      <span className={`inline-block px-3 py-1 rounded-full text-white font-semibold ${totalSpend.change_direction === 'increase' ? 'bg-red-500' : 'bg-green-600'}`}>
                        {totalSpend.percentage_change > 0 ? '+' : ''}
                        {totalSpend.percentage_change}% {totalSpend.change_direction === 'increase' ? '↑' : '↓'}
                      </span>
                    </div>
                  </div>
                )}
                {/* Category Breakdown */}
                {categoryBreakdown && categoryBreakdown.length > 0 && (
                  <div className="mb-4">
                    <div className="font-semibold mb-2">Category Breakdown (Pie):</div>
                    <div className="overflow-x-auto">
                      <table className="min-w-[400px] w-full text-sm">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left">Category</th>
                            <th className="px-2 py-1 text-right">Amount</th>
                            <th className="px-2 py-1 text-right">%</th>
                            <th className="px-2 py-1 text-right">Count</th>
                          </tr>
                        </thead>
                        <tbody>
                          {categoryBreakdown.map((row, idx) => (
                            <tr key={row.category + idx}>
                              <td className="px-2 py-1">{row.category}</td>
                              <td className="px-2 py-1 text-right">৳{row.amount}</td>
                              <td className="px-2 py-1 text-right">{row.percentage}%</td>
                              <td className="px-2 py-1 text-right">{row.transaction_count}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                {/* Category Trend */}
                {categoryTrend && categoryTrend.length > 0 && (
                  <div className="mb-4">
                    <div className="font-semibold mb-2">Category Trend (Last 6 months):</div>
                    <div className="overflow-x-auto">
                      <table className="min-w-[400px] w-full text-sm">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left">Month</th>
                            <th className="px-2 py-1 text-left">Category</th>
                            <th className="px-2 py-1 text-right">Amount</th>
                            <th className="px-2 py-1 text-right">%</th>
                          </tr>
                        </thead>
                        <tbody>
                          {categoryTrend.map((row, idx) => (
                            <tr key={row.month + row.category + idx}>
                              <td className="px-2 py-1">{row.month}</td>
                              <td className="px-2 py-1">{row.category}</td>
                              <td className="px-2 py-1 text-right">৳{row.amount}</td>
                              <td className="px-2 py-1 text-right">{row.percentage}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                {/* Spend Trend */}
                {spendTrend && spendTrend.length > 0 && (
                  <div className="mb-4">
                    <div className="font-semibold mb-2">Spend Trend (Last 180 days):</div>
                    <div className="overflow-x-auto">
                      <table className="min-w-[400px] w-full text-sm">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left">Date</th>
                            <th className="px-2 py-1 text-right">Amount</th>
                            <th className="px-2 py-1 text-right">Count</th>
                          </tr>
                        </thead>
                        <tbody>
                          {spendTrend.map((row, idx) => (
                            <tr key={row.date + idx}>
                              <td className="px-2 py-1">{row.date}</td>
                              <td className="px-2 py-1 text-right">৳{row.amount}</td>
                              <td className="px-2 py-1 text-right">{row.transaction_count}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                {/* Top Transactions */}
                {topTransactions && topTransactions.length > 0 && (
                  <div className="mb-4">
                    <div className="font-semibold mb-2">Top Transactions (Monthly):</div>
                    <div className="overflow-x-auto">
                      <table className="min-w-[400px] w-full text-sm">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left">Date</th>
                            <th className="px-2 py-1 text-right">Amount</th>
                            <th className="px-2 py-1 text-left">Category</th>
                            <th className="px-2 py-1 text-left">Merchant</th>
                            <th className="px-2 py-1 text-left">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {topTransactions.map((row, idx) => (
                            <tr key={row.id}>
                              <td className="px-2 py-1">{row.date}</td>
                              <td className="px-2 py-1 text-right">৳{row.amount}</td>
                              <td className="px-2 py-1">{row.category}</td>
                              <td className="px-2 py-1">{row.merchant}</td>
                              <td className="px-2 py-1">{row.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
            {activeTab === 'recent' && (
              <div className="w-full flex justify-center">
                <div className="bg-white rounded-lg shadow-md overflow-hidden w-full max-w-6xl">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-center">Recent Expenses</h2>
                  </div>
                  <div className="overflow-y-auto" style={{ maxHeight: '780px' }}>
                    <div className="overflow-x-auto">
                      <table className="w-full min-w-[900px]">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                            <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {expenses.map((expense) => (
                            <tr key={expense.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{expense.date}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{expense.description}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                  {expense.category}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                                {getCurrencySymbol(expense.currency)}{expense.amount.toFixed(2)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-center">
                                <div className="flex justify-center space-x-2">
                                  <button
                                    onClick={() => handleEdit(expense.id)}
                                    className="inline-flex items-center px-2 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
                                    title="Edit expense"
                                  >
                                    <Edit />
                                    <span className="ml-1">Edit</span>
                                  </button>
                                  <button
                                    onClick={() => handleDelete(expense.id)}
                                    disabled={deletingId === expense.id}
                                    className="inline-flex items-center px-2 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    title="Delete expense"
                                  >
                                    <Trash />
                                    {deletingId === expense.id ? (
                                      <span className="ml-1 text-xs">Deleting...</span>
                                    ) : (
                                      <span className="ml-1">Delete</span>
                                    )}
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {expenses.length === 0 && (
                      <div className="text-center py-12">
                        <p className="text-gray-500">No expenses here.</p>
                        <p className="text-sm text-gray-400 mt-1">Add your first expense using the form above or voice input.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Chatbot Button and Panel */}
      {!chatOpen && (
        <button
          className="fixed bottom-6 right-6 rounded-full p-4 z-50 flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #5eead4 0%, #38bdf8 50%, #a78bfa 100%)',
            border: '2px solid #fff',
            boxShadow: '0 6px 32px 0 rgba(56,189,248,0.18), 0 1px 8px 0 rgba(80,0,200,0.10)',
            position: 'fixed',
            right: '1.5rem',
            bottom: '1.5rem',
            width: 72,
            height: 72,
          }}
          onClick={() => setChatOpen(true)}
          aria-label="Open chat"
        >
          <CopilotIcon size={52} />
        </button>
      )}
      <ChatbotPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        onParseText={aiParseText}
        onParseReceipt={aiParseReceipt}
        onParseVoice={aiParseVoice}
      />
    </div>
  );
};

export default ExpenseTracker;
