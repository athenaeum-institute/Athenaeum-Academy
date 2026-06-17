// ============================================================
// Athenaeum — Supabase Courses & Progress Service
// ============================================================

window.AthenaeumCourses = {

  // Fetch all published courses
  async fetchAllCourses() {
    const { data, error } = await window.supabaseClient
      .from('courses')
      .select('*, profiles:instructor_id(full_name, avatar_url)')
      .eq('is_published', true)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching courses:', error);
      throw error;
    }
    return data;
  },

  // Fetch a single course with its modules and lessons
  async fetchCourseById(courseId) {
    const { data, error } = await window.supabaseClient
      .from('courses')
      .select(`
        *,
        profiles:instructor_id(full_name, avatar_url),
        modules (
          id, title, order_index,
          lessons (id, title, video_url, duration_minutes, order_index, is_free_preview)
        )
      `)
      .eq('id', courseId)
      .single();

    if (error) {
      console.error('Error fetching course by ID:', error);
      throw error;
    }

    // Sort modules and lessons
    if (data.modules) {
      data.modules.sort((a, b) => a.order_index - b.order_index);
      data.modules.forEach(m => {
        if (m.lessons) {
          m.lessons.sort((a, b) => a.order_index - b.order_index);
        }
      });
    }

    return data;
  },

  // Fetch enrolled courses for a student
  async fetchEnrolledCourses(userId) {
    const { data, error } = await window.supabaseClient
      .from('enrollments')
      .select(`
        course_id,
        enrolled_at,
        courses (
          id, title, thumbnail_url, category, subject, price,
          profiles:instructor_id(full_name, avatar_url)
        )
      `)
      .eq('student_id', userId)
      .order('enrolled_at', { ascending: false });

    if (error) {
      console.error('Error fetching enrolled courses:', error);
      throw error;
    }
    return data;
  },

  // Enroll a student in a course
  async enrollStudent(userId, courseId) {
    const { data, error } = await window.supabaseClient
      .from('enrollments')
      .insert([
        { student_id: userId, course_id: courseId, payment_status: 'free' } // Free for now
      ])
      .select()
      .single();

    if (error) {
      if (error.code === '23505') { // Unique violation
        console.warn('Student is already enrolled in this course.');
        return null;
      }
      console.error('Error enrolling student:', error);
      throw error;
    }
    return data;
  },

  // Mark a lesson as complete, and award XP
  async markLessonComplete(userId, lessonId) {
    // 1. Check if already completed to avoid duplicate XP
    const { data: existingProgress } = await window.supabaseClient
      .from('user_progress')
      .select('*')
      .eq('student_id', userId)
      .eq('lesson_id', lessonId)
      .single();

    if (existingProgress && existingProgress.completed) {
      return { status: 'already_completed' };
    }

    // 2. Insert or update user_progress
    const { data: progressData, error: progressError } = await window.supabaseClient
      .from('user_progress')
      .upsert({
        student_id: userId,
        lesson_id: lessonId,
        completed: true,
        completed_at: new Date().toISOString(),
        xp_awarded: true
      }, { onConflict: 'student_id, lesson_id' })
      .select()
      .single();

    if (progressError) {
      console.error('Error saving lesson progress:', progressError);
      throw progressError;
    }

    // 3. Award XP in profiles table
    // Fetch current XP
    const { data: profileData } = await window.supabaseClient
      .from('profiles')
      .select('xp')
      .eq('id', userId)
      .single();
      
    const currentXp = profileData?.xp || 0;
    const newXp = currentXp + 50;

    const { error: profileError } = await window.supabaseClient
      .from('profiles')
      .update({ xp: newXp })
      .eq('id', userId);

    if (profileError) {
      console.error('Error awarding XP:', profileError);
      throw profileError;
    }

    return { status: 'success', xpAdded: 50, totalXp: newXp, progressData };
  },

  // Get student dashboard stats
  async getStudentDashboardStats(userId) {
    try {
      // Get enrolled count
      const { count: enrolledCount } = await window.supabaseClient
        .from('enrollments')
        .select('*', { count: 'exact', head: true })
        .eq('student_id', userId);

      // Get completed lessons count
      const { count: completedLessonsCount } = await window.supabaseClient
        .from('user_progress')
        .select('*', { count: 'exact', head: true })
        .eq('student_id', userId)
        .eq('completed', true);

      // Get XP from profile
      const { data: profile } = await window.supabaseClient
        .from('profiles')
        .select('xp, full_name, avatar_url')
        .eq('id', userId)
        .single();

      return {
        enrolledCount: enrolledCount || 0,
        completedLessonsCount: completedLessonsCount || 0,
        xp: profile?.xp || 0,
        profile: profile
      };
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      return null;
    }
  },

  // Fetch top 10 leaderboard
  async getLeaderboard() {
    const { data, error } = await window.supabaseClient
      .from('profiles')
      .select('id, full_name, avatar_url, xp, role')
      .eq('role', 'Student')
      .order('xp', { ascending: false })
      .limit(10);

    if (error) {
      console.error('Error fetching leaderboard:', error);
      throw error;
    }
    return data;
  },

  // Fetch all completed lessons for a user (useful for syllabus checkmarks)
  async fetchCompletedLessons(userId) {
    const { data, error } = await window.supabaseClient
      .from('user_progress')
      .select('lesson_id')
      .eq('student_id', userId)
      .eq('completed', true);
      
    if (error) {
      console.error('Error fetching completed lessons:', error);
      return [];
    }
    return data.map(p => p.lesson_id);
  }
};
