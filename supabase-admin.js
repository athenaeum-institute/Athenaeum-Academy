/**
 * supabase-admin.js
 * Admin-specific API calls to Supabase.
 */

window.AthenaeumAdmin = (function() {
  
  function getClient() {
    if (!window.supabaseClient) {
      console.error("Supabase client not initialized.");
      return null;
    }
    return window.supabaseClient;
  }

  return {
    
    // -----------------------------------------------------
    // DASHBOARD STATS
    // -----------------------------------------------------
    async getDashboardStats() {
      const sb = getClient();
      if (!sb) return null;

      try {
        // 1. Total Students
        const { count: totalStudents, error: e1 } = await sb
          .from('profiles')
          .select('id', { count: 'exact', head: true })
          .eq('role', 'student');
        if (e1) throw e1;

        // 2. Paid Students
        const { count: paidStudents, error: e2 } = await sb
          .from('profiles')
          .select('id', { count: 'exact', head: true })
          .eq('role', 'student')
          .eq('plan_type', 'paid');
        if (e2) throw e2;

        // 3. Total Courses
        const { count: totalCourses, error: e3 } = await sb
          .from('courses')
          .select('id', { count: 'exact', head: true });
        if (e3) throw e3;

        // 4. Total Teachers
        const { count: totalTeachers, error: e4_teacher } = await sb
          .from('profiles')
          .select('id', { count: 'exact', head: true })
          .eq('role', 'teacher');
        if (e4_teacher) throw e4_teacher;

        // Fetch AI Usage for today
        const today = new Date().toISOString().split('T')[0];
        const { data: usageData, error: e4 } = await sb
          .from('ai_usage')
          .select('questions_used, quizzes_used, user_id')
          .eq('usage_date', today);
        if (e4) throw e4;

        let totalQuestions = 0;
        let totalQuizzes = 0;
        const activeAiUsers = new Set();
        
        if (usageData) {
          usageData.forEach(row => {
            totalQuestions += (row.questions_used || 0);
            totalQuizzes += (row.quizzes_used || 0);
            if (row.questions_used > 0 || row.quizzes_used > 0) {
              activeAiUsers.add(row.user_id);
            }
          });
        }

        return {
          totalStudents: totalStudents || 0,
          paidStudents: paidStudents || 0,
          totalCourses: totalCourses || 0,
          totalTeachers: totalTeachers || 0,
          aiQuestionsToday: totalQuestions,
          aiQuizzesToday: totalQuizzes,
          activeAiUsers: activeAiUsers.size,
          // Mock revenue
          totalRevenue: (paidStudents || 0) * 2499
        };
      } catch (err) {
        console.error("Error fetching admin stats:", err);
        return null;
      }
    },

    // -----------------------------------------------------
    // STUDENT MANAGEMENT
    // -----------------------------------------------------
    async fetchStudents(filter = 'all', searchQuery = '') {
      const sb = getClient();
      if (!sb) return [];

      try {
        let query = sb.from('profiles').select('*').eq('role', 'student').order('created_at', { ascending: false });
        
        if (filter !== 'all') {
          query = query.eq('plan_type', filter);
        }
        
        const { data, error } = await query;
        if (error) throw error;

        // Fetch AI Usage for today
        const today = new Date().toISOString().split('T')[0];
        const { data: usageData } = await sb.from('ai_usage').select('*').eq('usage_date', today);
        const usageMap = {};
        if (usageData) {
          usageData.forEach(u => usageMap[u.user_id] = u);
        }

        // Fetch Enrollments for courses
        const { data: enrollmentsData } = await sb.from('enrollments').select('student_id, course_id, payment_status, courses(title)');
        const enrollmentsMap = {};
        if (enrollmentsData) {
          enrollmentsData.forEach(e => {
            if (!enrollmentsMap[e.student_id]) enrollmentsMap[e.student_id] = [];
            enrollmentsMap[e.student_id].push({
              course_id: e.course_id,
              title: e.courses?.title || 'Unknown Course',
              payment_status: e.payment_status
            });
          });
        }

        let students = data.map(p => ({
          ...p,
          usage: usageMap[p.id] || { questions_used: 0, quizzes_used: 0 },
          enrollments: enrollmentsMap[p.id] || []
        }));
        
        if (searchQuery) {
          const lowerQuery = searchQuery.toLowerCase();
          students = students.filter(s => 
            (s.full_name && s.full_name.toLowerCase().includes(lowerQuery)) ||
            (s.email && s.email.toLowerCase().includes(lowerQuery))
          );
        }
        return students || [];
      } catch (err) {
        console.error("Error fetching students:", err);
        return [];
      }
    },

    async updateStudentPlan(userId, newPlan) {
      const sb = getClient();
      if (!sb) return { status: 'error', message: 'Client not ready' };
      
      try {
        const { error } = await sb.rpc('admin_update_plan', { 
          target_user_id: userId, 
          new_plan: newPlan 
        });
        if (error) throw error;

        return { status: 'success' };
      } catch (err) {
        console.error("Error updating plan:", err);
        return { status: 'error', message: err.message };
      }
    },

    async updateEnrollmentStatus(studentId, courseId, newStatus) {
      const sb = getClient();
      if (!sb) return { status: 'error', message: 'Client not ready' };
      
      try {
        const { error } = await sb.rpc('admin_update_enrollment_status', { 
          target_student_id: studentId, 
          target_course_id: courseId, 
          new_status: newStatus 
        });
          
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error updating enrollment:", err);
        return { status: 'error', message: err.message };
      }
    },

    async toggleStudentStatus(userId, statusParam) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      
      try {
        let newStatus = 'active';
        if (statusParam === true || statusParam === 'blocked') newStatus = 'blocked';
        if (statusParam === 'deleted' || statusParam === 'delete') newStatus = 'deleted';

        if (newStatus === 'deleted') {
          // Hard delete the user via RPC to allow them to register again
          const { error } = await sb.rpc('admin_hard_delete_user', { target_user_id: userId });
          if (error) throw error;
          return { status: 'success' };
        }

        const { error } = await sb.rpc('admin_update_status', { 
          target_user_id: userId, 
          new_status: newStatus 
        });
        if (error) throw error;

        return { status: 'success' };
      } catch (err) {
        console.error("Error toggling status:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // COURSE MANAGEMENT
    // -----------------------------------------------------
    async fetchAllCourses() {
      const sb = getClient();
      if (!sb) return [];
      try {
        const { data, error } = await sb.from('courses').select('*, profiles(full_name, avatar_url)').order('created_at', { ascending: false });
        if (error) throw error;
        // Map to expected structure
        return data.map(c => ({
          ...c,
          instructorName: c.profiles?.full_name || 'Admin',
          instructorAvatar: c.profiles?.avatar_url || ''
        }));
      } catch (err) {
        console.error("Error fetching courses:", err);
        return [];
      }
    },

    async saveCourse(courseData) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      
      try {
        let error;
        if (courseData.id) {
          // Update
          const { error: updErr } = await sb.from('courses').update(courseData).eq('id', courseData.id);
          error = updErr;
        } else {
          // Insert
          const { error: insErr } = await sb.from('courses').insert([courseData]);
          error = insErr;
        }
        
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error saving course:", err);
        return { status: 'error', message: err.message };
      }
    },
    
    async deleteCourse(courseId) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { error } = await sb.from('courses').delete().eq('id', courseId);
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error deleting course:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // TEACHERS
    // -----------------------------------------------------
    async fetchTeachers() {
      const sb = getClient();
      if (!sb) return [];
      try {
        const { data, error } = await sb.from('profiles').select('*').in('role', ['Teacher', 'teacher', 'pending_teacher']);
        if (error) throw error;
        return data || [];
      } catch (err) {
        console.error("Error fetching teachers:", err);
        return [];
      }
    },

    async updateTeacherRole(userId, newRole) {
      const sb = getClient();
      if (!sb) return { status: 'error', message: 'Client not ready' };
      try {
        const { error } = await sb.from('profiles').update({ role: newRole }).eq('id', userId);
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error updating teacher role:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // ANNOUNCEMENTS
    // -----------------------------------------------------
    async fetchAnnouncements() {
      const sb = getClient();
      if (!sb) return [];
      try {
        const { data, error } = await sb.from('announcements').select('*').order('created_at', { ascending: false });
        if (error) throw error;
        return data || [];
      } catch (err) {
        console.error("Error fetching announcements:", err);
        return [];
      }
    },
    
    async saveAnnouncement(title, message, target, type = 'info', isPinned = false) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { error } = await sb.from('announcements').insert([{ title, message, target, type, is_pinned: isPinned }]);
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error saving announcement:", err);
        return { status: 'error', message: err.message };
      }
    },
    
    async toggleAnnouncementStatus(id, isActive) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { error } = await sb.from('announcements').update({ is_active: isActive }).eq('id', id);
        if (error) throw error;
        return { status: 'success' };
      } catch (err) {
        console.error("Error toggling announcement:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // LIVE CLASSES
    // -----------------------------------------------------
    async getLiveClasses() {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { data, error } = await sb.from('live_classes').select('*, courses(title)').order('start_time', { ascending: false });
        if (error) throw error;
        return { status: 'success', data };
      } catch (err) {
        console.error("Error fetching live classes:", err);
        return { status: 'error', message: err.message };
      }
    },
    
    async saveLiveClass(classData) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        let result;
        if (classData.id) {
          result = await sb.from('live_classes').update(classData).eq('id', classData.id).select().single();
        } else {
          result = await sb.from('live_classes').insert([classData]).select().single();
        }
        if (result.error) throw result.error;
        return { status: 'success', data: result.data };
      } catch (err) {
        console.error("Error saving live class:", err);
        return { status: 'error', message: err.message };
      }
    },

    async deleteLiveClass(id) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        // Use RPC to bypass RLS securely
        const { data, error } = await sb.rpc('admin_delete_live_class', { class_id: id });
        
        if (error) {
          if (error.message.includes('Could not find function')) {
            return { status: 'error', message: 'Function missing! You MUST run the force-delete-rpc.sql script in Supabase SQL Editor.' };
          }
          throw error;
        }
        
        if (data === false) {
           return { status: 'error', message: 'Access Denied by RPC. You are not recognized as an admin.' };
        }
        
        return { status: 'success' };
      } catch (err) {
        console.error("Error deleting live class:", err);
        return { status: 'error', message: err.message };
      }
    },

    async getAllTeachers() {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { data, error } = await sb.from('profiles').select('id, full_name').ilike('role', '%eacher%');
        if (error) throw error;
        return { status: 'success', data };
      } catch (err) {
        console.error("Error fetching teachers:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // FREE TRIAL REQUESTS
    // -----------------------------------------------------
    async getFreeTrialRequests() {
      const sb = getClient();
      if (!sb) return [];
      try {
        const { data, error } = await sb.from('free_trial_requests').select('*').order('created_at', { ascending: false });
        if (error) throw error;
        return data || [];
      } catch (err) {
        console.error("Error fetching free trials:", err);
        return [];
      }
    },

    async updateFreeTrialStatus(id, newStatus) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { error } = await sb.from('free_trial_requests').update({ status: newStatus }).eq('id', id);
        if (error) throw error;
        
        // Auto-enroll student when admin confirms
        if (newStatus === 'confirmed') {
          const { data: req } = await sb.from('free_trial_requests').select('user_id, course_name').eq('id', id).single();
          if (req && req.user_id && req.course_name) {
            const searchPattern = '%' + req.course_name.replace(/\\s+/g, '%') + '%';
            const { data: courses } = await sb.from('courses').select('id').ilike('title', searchPattern).limit(1);
            if (courses && courses.length > 0) {
              const { error: enrollErr } = await sb.from('enrollments').insert({
                student_id: req.user_id,
                course_id: courses[0].id,
                payment_status: 'free'
              });
              if (enrollErr && enrollErr.code !== '23505') { // ignore duplicate unique constraint
                console.warn("Could not auto-enroll:", enrollErr);
              }
            }
          }
        }
        
        return { status: 'success' };
      } catch (err) {
        console.error("Error updating free trial:", err);
        return { status: 'error', message: err.message };
      }
    },

    // -----------------------------------------------------
    // TEACHER CODES
    // -----------------------------------------------------
    async fetchTeacherCodes() {
      const sb = getClient();
      if (!sb) return [];
      try {
        const { data, error } = await sb
          .from('teacher_access_codes')
          .select(`*, courses(title)`)
          .order('created_at', { ascending: false });
        if (error) throw error;
        return data || [];
      } catch (err) {
        console.error("Error fetching teacher codes:", err);
        return [];
      }
    },

    async generateTeacherCode(courseId) {
      const sb = getClient();
      if (!sb) return { status: 'error' };
      try {
        const { data, error } = await sb.rpc('generate_teacher_code', { target_course_id: courseId });
        if (error) throw error;
        return { status: 'success', code: data };
      } catch (err) {
        console.error("Error generating teacher code:", err);
        return { status: 'error', message: err.message };
      }
    }

  };
})();
