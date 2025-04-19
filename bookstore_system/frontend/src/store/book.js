import { defineStore } from 'pinia';
import { getBooks, getBook, createBook, updateBook, deleteBook } from '../api/books';

export const useBookStore = defineStore('book', {
  state: () => ({
    books: [], // 书籍列表
    currentBook: null, // 当前选中的书籍
    pagination: {
      page: 1,
      per_page: 20,
      total: 0,
      pages: 0
    },
    loading: false, // 是否正在加载数据
    error: null, // 错误信息
    searchParams: { // 搜索参数
      search: '',
      page: 1,
      per_page: 20,
      active_only: true
    }
  }),
  
  getters: {
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error
  },
  
  actions: {
    /**
     * 加载书籍列表
     * @param {Object} params 可选的查询参数，默认使用state中的searchParams
     */
    async loadBooks(params = {}) {
      // 合并默认参数和传入参数
      const searchParams = { ...this.searchParams, ...params };
      // 更新当前使用的搜索参数
      this.searchParams = searchParams;
      
      this.loading = true;
      this.error = null;
      
      try {
        const result = await getBooks(searchParams);
        this.books = result.books;
        this.pagination = result.pagination;
        return result;
      } catch (error) {
        this.error = error.message;
        console.error('加载书籍列表失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载单本书籍详情
     * @param {string|number} id 书籍ID或ISBN
     */
    async loadBook(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const book = await getBook(id);
        this.currentBook = book;
        return book;
      } catch (error) {
        this.error = error.message;
        console.error('加载书籍详情失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 创建新书籍
     * @param {Object} bookData 书籍数据
     */
    async addBook(bookData) {
      this.loading = true;
      this.error = null;
      
      try {
        const book = await createBook(bookData);
        
        // 可选：将新书籍添加到列表开头（如果当前页是第一页）
        if (this.pagination.page === 1) {
          this.books.unshift(book);
          
          // 保持列表长度一致
          if (this.books.length > this.pagination.per_page) {
            this.books.pop();
          }
          
          // 更新总数
          this.pagination.total += 1;
          // 更新总页数
          this.pagination.pages = Math.ceil(this.pagination.total / this.pagination.per_page);
        }
        
        return book;
      } catch (error) {
        this.error = error.message;
        console.error('创建书籍失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 更新书籍信息
     * @param {number} id 书籍ID
     * @param {Object} bookData 书籍数据
     */
    async editBook(id, bookData) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedBook = await updateBook(id, bookData);
        
        // 更新当前选中的书籍
        if (this.currentBook && this.currentBook.id === id) {
          this.currentBook = updatedBook;
        }
        
        // 更新列表中的书籍
        const index = this.books.findIndex(book => book.id === id);
        if (index !== -1) {
          this.books[index] = updatedBook;
        }
        
        return updatedBook;
      } catch (error) {
        this.error = error.message;
        console.error('更新书籍失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 删除书籍（逻辑删除）
     * @param {number} id 书籍ID
     */
    async removeBook(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await deleteBook(id);
        
        // 从列表中移除删除的书籍
        if (this.searchParams.active_only) {
          this.books = this.books.filter(book => book.id !== id);
          this.pagination.total -= 1;
          this.pagination.pages = Math.ceil(this.pagination.total / this.pagination.per_page);
        } else {
          // 如果显示的是所有书籍（包括被删除的），则只更新状态
          const index = this.books.findIndex(book => book.id === id);
          if (index !== -1) {
            this.books[index].is_active = false;
          }
        }
        
        // 清除当前选中的书籍（如果是已删除的书籍）
        if (this.currentBook && this.currentBook.id === id) {
          this.currentBook = null;
        }
        
        return result;
      } catch (error) {
        this.error = error.message;
        console.error('删除书籍失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 设置搜索参数
     * @param {Object} params 搜索参数
     */
    setSearchParams(params) {
      this.searchParams = { ...this.searchParams, ...params };
    },
    
    /**
     * 重置当前选中的书籍
     */
    resetCurrentBook() {
      this.currentBook = null;
    },
    
    /**
     * 清除错误信息
     */
    clearError() {
      this.error = null;
    }
  }
});

