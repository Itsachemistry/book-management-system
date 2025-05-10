import { defineStore } from 'pinia';
import { getBooks, getBook, createBook, updateBook, deleteBook, getBookByIsbn } from '../api/books';

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
      console.log('[Store Action - loadBooks] 开始加载书籍, 参数:', searchParams);
      
      try {
        // 1. 检查 API 调用和参数 (getBooks 在 api/books.js 中调用 /api/books)
        const result = await getBooks(searchParams);
        // 2. 打印完整的 API 响应数据
        console.log('[Store Action - loadBooks] 收到 API 响应:', JSON.stringify(result, null, 2));
        
        // 3. 修正从 response.data 提取数据的方式
        //    后端返回的是 result.items 和分散的分页字段
        if (result && Array.isArray(result.items)) {
          this.books = result.items;
          this.pagination = {
            page: result.page,
            per_page: result.per_page,
            total: result.total,
            pages: result.pages
          };
        } else {
          console.warn('[Store Action - loadBooks] API 响应格式不符合预期:', result);
          this.books = []; // 清空或保持旧数据？这里选择清空
          this.pagination = { page: 1, per_page: 20, total: 0, pages: 0 }; // 重置分页
        }

        // 4. 打印更新后的 state
        console.log('[Store Action - loadBooks] 更新后 state.books:', JSON.stringify(this.books, null, 2));
        console.log('[Store Action - loadBooks] 更新后 state.pagination:', JSON.stringify(this.pagination, null, 2));
        
        return result; // 返回原始结果或处理后的数据，取决于调用者需要什么
      } catch (error) {
        this.error = error.message;
        console.error('[Store Action - loadBooks] 加载书籍列表失败:', error);
        // 清空数据以避免显示旧的或错误的数据
        this.books = [];
        this.pagination = { page: 1, per_page: 20, total: 0, pages: 0 };
        throw error;
      } finally {
        this.loading = false;
        console.log('[Store Action - loadBooks] 加载结束');
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
     * 通过ISBN加载书籍
     * @param {string} isbn 书籍ISBN
     */
    async loadBookByIsbn(isbn) {
      this.loading = true;
      this.error = null;
      
      try {
        const book = await getBookByIsbn(isbn);
        // 不设置为currentBook，因为这只是为了搜索
        return book;
      } catch (error) {
        console.error('通过ISBN加载书籍失败:', error);
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
      console.log('addBook payload →', bookData);
      this.loading = true;
      this.error = null;
      
      try {
        const book = await createBook(bookData);
        
        // 确保 books 是数组并且 pagination 存在且有效
        if (Array.isArray(this.books) && this.pagination && typeof this.pagination.page === 'number') {
          // 可选：将新书籍添加到列表开头（如果当前页是第一页）
          if (this.pagination.page === 1) {
            this.books.unshift(book);
            
            // 确保 per_page 是有效数字
            if (typeof this.pagination.per_page === 'number' && this.pagination.per_page > 0) {
              // 保持列表长度一致
              if (this.books.length > this.pagination.per_page) {
                this.books.pop();
              }
              
              // 确保 total 是有效数字
              if (typeof this.pagination.total === 'number') {
                // 更新总数
                this.pagination.total += 1;
                // 更新总页数
                this.pagination.pages = Math.ceil(this.pagination.total / this.pagination.per_page);
              } else {
                 console.warn('addBook: pagination.total is not a number. Skipping total/pages update.');
                 // 可以考虑重新加载书籍列表以获取正确的 total
                 // this.loadBooks(); 
              }
            } else {
              console.warn('addBook: pagination.per_page is invalid. Skipping list length adjustment and pages update.');
            }
          }
        } else {
           console.warn('addBook: State (books or pagination) is not ready for update. Skipping local state update.');
           // 考虑在添加成功后强制刷新列表
           // this.loadBooks(); 
        }
        
        return book;
      } catch (error) {
        // 调试用：打印后端返回的详细信息
        console.error('addBook caught error:', error);
        console.error('addBook error.response.data:', error.response?.data);
        // 抛出更具体的错误信息，而不是原始的 error.message，因为它可能来自 API 调用
        // 如果错误发生在状态更新阶段，error.message 可能不准确
        this.error = '添加书籍后更新前端状态失败: ' + (error instanceof Error ? error.message : String(error));
        throw new Error(this.error); // 重新抛出包装后的错误
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
        // 过滤数据，只保留后端接受的字段，移除isbn字段
        const validFields = {
          name: bookData.name,
          author: bookData.author || '',
          publisher: bookData.publisher || '',
          retail_price: Number(bookData.retail_price),
          quantity: Number(bookData.quantity),
          is_active: Boolean(bookData.is_active)
        };
        
        // 添加详细日志
        console.log(`准备更新书籍(ID: ${id})，过滤后数据:`, validFields);
        const updatedBook = await updateBook(id, validFields);
        console.log('书籍更新成功，返回数据:', updatedBook);
        
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
     * 删除书籍（物理删除）
     * @param {number} id 书籍ID
     */
    async removeBook(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await deleteBook(id);
        
        // 从列表中完全移除被删除的书籍
        this.books = this.books.filter(book => book.id !== id);
        
        // 更新分页信息
        if (this.pagination && typeof this.pagination.total === 'number') {
          this.pagination.total -= 1;
          this.pagination.pages = Math.ceil(this.pagination.total / this.pagination.per_page);
        }
        
        // 如果当前选中的书籍是被删除的书籍，清除选择
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

