// ─────────────────────────────────────────────────────────────
// Supabase Service Class for Teacher Dashboard
// Contains all database logic required for dashboard-teacher.html
// ─────────────────────────────────────────────────────────────

class AthenaeumTeacherService {
  constructor() {
    this.client = window.supabaseClient;
  }

  async getTeacherId() {
    const { data: { session } } = await this.client.auth.getSession();
    return session?.user?.id || null;
  }

  // ── STATS ──
  async getDashboardStats() {
    const tid = await this.getTeacherId();
    if (!tid) return null;

    // Get teacher's courses
    const { data: courses, error: cErr } = await this.client.from('courses').select('id').eq('instructor_id', tid);
    if (cErr) throw cErr;
    const courseIds = courses.map(c => c.id);

    let enrolledCount = 0;
    if (courseIds.length > 0) {
      const { count: eCount, error: eErr } = await this.client.from('enrollments')
        .select('*', { count: 'exact', head: true })
        .in('course_id', courseIds);
      if (!eErr) enrolledCount = eCount || 0;
    }

    let lessonsCount = 0;
    if (courseIds.length > 0) {
      // Find modules for these courses
      const { data: modules } = await this.client.from('modules').select('id').in('course_id', courseIds);
      const moduleIds = modules ? modules.map(m => m.id) : [];
      if (moduleIds.length > 0) {
        const { count: lCount } = await this.client.from('lessons')
          .select('*', { count: 'exact', head: true })
          .in('module_id', moduleIds);
        lessonsCount = lCount || 0;
      }
    }

    return {
      totalCourses: courseIds.length,
      totalStudents: enrolledCount,
      totalLessons: lessonsCount,
      avgRating: 4.8 // Mockup as requested
    };
  }

  // ── COURSES ──
  async getMyCourses() {
    const tid = await this.getTeacherId();
    if (!tid) return [];
    
    // Fetch courses with enrollment counts
    const { data: courses, error } = await this.client.from('courses')
      .select(`
        *,
        enrollments (count)
      `)
      .eq('instructor_id', tid)
      .order('created_at', { ascending: false });
      
    if (error) throw error;
    return courses;
  }

  async saveCourse(courseData) {
    const tid = await this.getTeacherId();
    if (!tid) throw new Error('Not authenticated');

    const payload = {
      title: courseData.title,
      description: courseData.description,
      category: courseData.category,
      subject: courseData.subject,
      price: courseData.price || 0,
      thumbnail_url: courseData.thumbnail_url,
      is_published: courseData.is_published || false,
      instructor_id: tid
    };

    if (courseData.id) {
      const { data, error } = await this.client.from('courses').update(payload).eq('id', courseData.id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('courses').insert([payload]).select().single();
      if (error) throw error;
      return data;
    }
  }

  async deleteCourse(id) {
    const { error } = await this.client.from('courses').delete().eq('id', id);
    if (error) throw error;
    return true;
  }

  async toggleCoursePublish(id, isPublished) {
    const { error } = await this.client.from('courses').update({ is_published: isPublished }).eq('id', id);
    if (error) throw error;
    return true;
  }

  // ── MODULES ──
  async getModules(courseId) {
    const { data, error } = await this.client.from('modules').select('*').eq('course_id', courseId).order('order_index', { ascending: true });
    if (error) throw error;
    return data;
  }

  async saveModule(id, courseId, title, orderIndex) {
    if (id) {
      const { data, error } = await this.client.from('modules').update({ title, order_index: orderIndex }).eq('id', id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('modules').insert([{ course_id: courseId, title, order_index: orderIndex }]).select().single();
      if (error) throw error;
      return data;
    }
  }

  async deleteModule(id) {
    const { error } = await this.client.from('modules').delete().eq('id', id);
    if (error) throw error;
    return true;
  }

  // ── LESSONS ──
  async getLessons(moduleId) {
    const { data, error } = await this.client.from('lessons').select('*').eq('module_id', moduleId).order('order_index', { ascending: true });
    if (error) throw error;
    return data;
  }

  async saveLesson(lessonData) {
    if (lessonData.id) {
      const { data, error } = await this.client.from('lessons').update(lessonData).eq('id', lessonData.id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('lessons').insert([lessonData]).select().single();
      if (error) throw error;
      return data;
    }
  }

  async deleteLesson(id) {
    const { error } = await this.client.from('lessons').delete().eq('id', id);
    if (error) throw error;
    return true;
  }

  // ── STUDENTS ──
  async getMyStudents() {
    const tid = await this.getTeacherId();
    if (!tid) return [];

    try {
      // Find all courses by this teacher
      const { data: courses } = await this.client.from('courses').select('id, title').eq('instructor_id', tid);
      if (!courses || courses.length === 0) return [];
      
      const courseIds = courses.map(c => c.id);
      const courseMap = {};
      courses.forEach(c => courseMap[c.id] = c.title);

      // Get all enrollments for these courses
      const { data: enrollments, error } = await this.client.from('enrollments')
        .select('*')
        .in('course_id', courseIds)
        .order('enrolled_at', { ascending: false });

      if (error) throw error;
      if (!enrollments || enrollments.length === 0) return [];

      // Get the profiles manually since auth.users is restricted and profiles lacks email
      const studentIds = [...new Set(enrollments.map(e => e.student_id))];
      const { data: profiles, error: pErr } = await this.client.from('profiles').select('id, full_name, plan_type').in('id', studentIds);
      
      if (pErr) console.warn("Could not fetch profiles:", pErr);

      const profileMap = {};
      if (profiles) profiles.forEach(p => profileMap[p.id] = p);

      return enrollments.map(e => ({
        ...e,
        course_title: courseMap[e.course_id],
        student: {
          full_name: profileMap[e.student_id]?.full_name || 'Unknown',
          plan_type: profileMap[e.student_id]?.plan_type || 'trial',
          email: 'Hidden (Privacy)' // Teachers cannot directly query auth.users email
        }
      }));
    } catch (err) {
      console.error("Error fetching students:", err);
      throw err;
    }
  }

  // ── ANNOUNCEMENTS ──
  async getAnnouncements() {
    const tid = await this.getTeacherId();
    if (!tid) return [];
    
    // Admin global ones or teacher's course ones
    const { data: courses } = await this.client.from('courses').select('id').eq('instructor_id', tid);
    const courseIds = courses ? courses.map(c => c.id) : [];
    
    // We fetch global admin ones AND ones where course_id IN (teacher's courses)
    // Actually simpler: just fetch announcements where target='all' OR course_id is in teacher's courses
    
    let query = this.client.from('announcements').select(`*, courses(title)`).order('created_at', { ascending: false });
    const { data, error } = await query;
    if (error) throw error;
    
    // Filter manually for safety: global OR teacher's specific course
    return data.filter(a => ['all','paid','trial','free'].includes(a.target) || courseIds.includes(a.course_id));
  }

  async postAnnouncement(courseId, title, message) {
    const { error } = await this.client.from('announcements').insert([{
      title,
      message,
      target: courseId, // saving course_id as target is fine since target is now unrestricted, OR we save into course_id column
      course_id: courseId,
      is_active: true
    }]);
    if (error) throw error;
    return true;
  }

  // ── MOCK EXAMS ──
  async getMyExams() {
    const tid = await this.getTeacherId();
    if (!tid) return [];
    const { data, error } = await this.client.from('exams').select('*, courses(title)').eq('teacher_id', tid).order('created_at', { ascending: false });
    if (error) throw error;
    return data;
  }

  async saveExam(examData) {
    const tid = await this.getTeacherId();
    examData.teacher_id = tid;
    
    if (examData.id) {
      const { data, error } = await this.client.from('exams').update(examData).eq('id', examData.id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('exams').insert([examData]).select().single();
      if (error) throw error;
      return data;
    }
  }

  async getExamQuestions(examId) {
    const { data, error } = await this.client.from('exam_questions').select('*').eq('exam_id', examId).order('order_index', { ascending: true });
    if (error) throw error;
    return data;
  }

  async saveQuestion(qData) {
    if (qData.id) {
      const { data, error } = await this.client.from('exam_questions').update(qData).eq('id', qData.id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('exam_questions').insert([qData]).select().single();
      if (error) throw error;
      return data;
    }
  }
  
  async deleteQuestion(id) {
      const { error } = await this.client.from('exam_questions').delete().eq('id', id);
      if (error) throw error;
      return true;
  }

  // ── LIVE CLASSES ──
  async getMyLiveClasses() {
    const tid = await this.getTeacherId();
    if (!tid) return [];

    const { data: courses } = await this.client.from('courses').select('id, title, subject').eq('instructor_id', tid);
    if (!courses || courses.length === 0) return [];
    
    const courseIds = courses.map(c => c.id);
    const courseMap = {};
    courses.forEach(c => courseMap[c.id] = c);

    const { data: classes, error } = await this.client.from('live_classes')
      .select('*')
      .in('course_id', courseIds)
      .order('start_time', { ascending: false });

    if (error) throw error;
    
    return classes.map(c => ({
      ...c,
      course_title: courseMap[c.course_id].title
    }));
  }

  async saveLiveClass(classData) {
    if (classData.id) {
      const { data, error } = await this.client.from('live_classes').update(classData).eq('id', classData.id).select().single();
      if (error) throw error;
      return data;
    } else {
      const { data, error } = await this.client.from('live_classes').insert([classData]).select().single();
      if (error) throw error;
      return data;
    }
  }

  async deleteLiveClass(id) {
    const { error } = await this.client.from('live_classes').delete().eq('id', id);
    if (error) throw error;
    return true;
  }
}

// Initialize on window
window.AthenaeumTeacher = new AthenaeumTeacherService();
