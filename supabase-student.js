// ─────────────────────────────────────────────────────────────
// Supabase Service Class for Student Dashboard
// Contains all database logic required for dashboard-student.html
// ─────────────────────────────────────────────────────────────

class AthenaeumStudentService {
  constructor() {
    this.client = window.supabaseClient;
  }

  async getStudentId() {
    const { data: { session } } = await this.client.auth.getSession();
    return session?.user?.id || null;
  }

  // ── UPDATE STREAK ──
  async updateStreak() {
    const { data, error } = await this.client.rpc('update_student_streak');
    if (error) {
      console.error("Streak update error:", error);
      return null;
    }
    return data; // { streak, bonus, is_milestone, updated }
  }

  // ── FETCH DASHBOARD DATA ──
  async getDashboardData() {
    const sid = await this.getStudentId();
    if (!sid) throw new Error("Not logged in");

    // We will fetch all data in parallel using Promise.all
    
    // 1. Profile Data
    const pProfile = this.client.from('profiles').select('*').eq('id', sid).single();
    
    // 2. Enrolled Courses
    const pCourses = this.client.from('enrollments')
      .select('course_id, courses(id, title, category, subject, thumbnail_url)')
      .eq('student_id', sid)
      .order('enrolled_at', { ascending: false });

    // 3. User Progress (for lessons completed and Last Lesson)
    const pProgress = this.client.from('user_progress')
      .select('lesson_id, completed, updated_at, lessons(title, module_id, modules(course_id, courses(title)))')
      .eq('student_id', sid)
      .order('updated_at', { ascending: false });

    // 4. Exam Results
    const pExams = this.client.from('exam_results')
      .select('percentage, score, total_marks, completed_at, exams(title)')
      .eq('student_id', sid)
      .order('completed_at', { ascending: false });

    // 5. Announcements (Active)
    const pAnnouncements = this.client.from('announcements')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false });

    // Resolve all
    const [resProfile, resCourses, resProgress, resExams, resAnn] = await Promise.all([
      pProfile, pCourses, pProgress, pExams, pAnnouncements
    ]);

    if (resProfile.error) throw resProfile.error;

    const profile = resProfile.data;
    const enrollments = resCourses.data || [];
    const progressData = resProgress.data || [];
    const examResults = resExams.data || [];
    const allAnnouncements = resAnn.data || [];

    // Process Courses
    const courses = enrollments.map(e => e.courses).filter(c => c !== null);

    // Process Lessons Completed
    const lessonsCompletedCount = progressData.filter(p => p.completed).length;

    // Last Lesson
    let lastLesson = null;
    if (progressData.length > 0) {
      const p = progressData[0]; // Most recent due to order
      lastLesson = {
        title: p.lessons?.title || 'Unknown Lesson',
        courseName: p.lessons?.modules?.courses?.title || 'Unknown Course',
        completed: p.completed
      };
    }

    // Process Exams Averages & Recent 3
    let avgExamScore = 0;
    if (examResults.length > 0) {
      const sum = examResults.reduce((acc, curr) => acc + curr.percentage, 0);
      avgExamScore = Math.round(sum / examResults.length);
    }
    const recentExams = examResults.slice(0, 3);

    // Process Announcements (filter by target)
    const planType = profile.plan_type || 'trial';
    const activeAnnouncements = allAnnouncements.filter(a => {
      // If target is all, planType, or a specific course the user is enrolled in
      if (a.target === 'all' || a.target === planType) return true;
      if (courses.some(c => c.id === a.target)) return true; // targeted to course ID
      return false;
    });

    return {
      profile,
      courses,
      stats: {
        totalCourses: courses.length,
        lessonsCompleted: lessonsCompletedCount,
        avgExamScore,
        examsAttempted: examResults.length
      },
      lastLesson,
      recentExams,
      announcements: activeAnnouncements
    };
  }

  // ── LEADERBOARD ──
  async getLeaderboard() {
    // Top 10 by XP
    const { data: top10, error } = await this.client.from('profiles')
      .select('id, full_name, xp')
      .order('xp', { ascending: false })
      .limit(10);
      
    if (error) throw error;
    
    // Check own rank if not in top 10
    const sid = await this.getStudentId();
    let ownRank = -1;
    
    const isInTop10 = top10.findIndex(p => p.id === sid);
    if (isInTop10 >= 0) {
      ownRank = isInTop10 + 1;
    } else {
      // Find position
      const { data: profile } = await this.client.from('profiles').select('xp').eq('id', sid).single();
      if (profile) {
        const { count } = await this.client.from('profiles').select('*', { count: 'exact', head: true }).gt('xp', profile.xp);
        ownRank = (count || 0) + 1;
      }
    }

    return { top10, ownRank, studentId: sid };
  }

  // ── LIVE CLASSES ──
  async getLiveClasses() {
    const { data, error } = await this.client.from('live_classes')
      .select('*, courses(title)')
      .order('start_time', { ascending: true });
      
    if (error) throw error;
    
    return data.map(c => ({
      ...c,
      course_title: c.courses ? c.courses.title : 'Course'
    }));
  }

  // ── NOTIFICATIONS ──
  async getNotifications() {
    const { data, error } = await this.client.from('notifications')
      .select('*')
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data;
  }

  async markNotificationRead(id) {
    const { error } = await this.client.from('notifications')
      .update({ is_read: true })
      .eq('id', id);
    if (error) throw error;
    return true;
  }

}

// Initialize on window
window.AthenaeumStudent = new AthenaeumStudentService();
