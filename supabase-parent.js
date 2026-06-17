// ─────────────────────────────────────────────────────────────
// Supabase Service Class for Parent Dashboard
// Contains all database logic required for dashboard-parent.html
// ─────────────────────────────────────────────────────────────

class AthenaeumParentService {
  constructor() {
    this.client = window.supabaseClient;
  }

  async getParentId() {
    const { data: { session } } = await this.client.auth.getSession();
    return session?.user?.id || null;
  }

  // 1. Get Parent Profile
  async getProfile() {
    const pid = await this.getParentId();
    if (!pid) return null;
    const { data, error } = await this.client.from('profiles').select('*').eq('id', pid).single();
    if (error) throw error;
    return data;
  }

  // 2. Link Child
  async linkChild(studentEmail) {
    const { data, error } = await this.client.rpc('link_child_by_email', { student_email: studentEmail });
    if (error) throw error;
    return data; // { success, message }
  }

  // 3. Get All Linked Children (Basic Info for tabs)
  async getLinkedChildren() {
    const pid = await this.getParentId();
    if (!pid) return [];

    const { data, error } = await this.client.from('parent_child_links')
      .select('student_id, is_verified, profiles!student_id(id, full_name, xp, plan_type, streak_days, last_login_date)')
      .eq('parent_id', pid)
      .eq('is_verified', true);
      
    if (error) throw error;
    return data.map(d => d.profiles).filter(p => p !== null);
  }

  // 4. Get Detailed Data for a specific child
  async getChildData(studentId) {
    if (!studentId) return null;

    // Parallel fetch: enrollments, progress, exams
    const pCourses = this.client.from('enrollments')
      .select('course_id, enrolled_at, courses(id, title, category, subject)')
      .eq('student_id', studentId);

    const pProgress = this.client.from('user_progress')
      .select('lesson_id, completed, updated_at, lessons(id, title, module_id, modules(course_id, courses(title)))')
      .eq('student_id', studentId);

    const pExams = this.client.from('exam_results')
      .select('score, total_marks, percentage, completed_at, xp_awarded, exams(id, title, courses(title))')
      .eq('student_id', studentId)
      .order('completed_at', { ascending: false });

    const [resCourses, resProgress, resExams] = await Promise.all([pCourses, pProgress, pExams]);

    const enrollments = resCourses.data || [];
    const progress = resProgress.data || [];
    const exams = resExams.data || [];

    // Aggregate Course Progress
    const courseStats = enrollments.map(e => {
      const course = e.courses;
      // Find all progress for this course
      const cProg = progress.filter(p => p.lessons?.modules?.course_id === course.id);
      const totalLessons = cProg.length; // Approximate, if progress rows exist
      const completedLessons = cProg.filter(p => p.completed).length;
      const pct = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;
      
      // Last watched
      const sortedProg = [...cProg].sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at));
      const lastWatched = sortedProg.length > 0 ? sortedProg[0].lessons?.title : 'Not started';
      const lastDate = sortedProg.length > 0 ? new Date(sortedProg[0].updated_at) : new Date(e.enrolled_at);

      return {
        ...course,
        progressPct: pct,
        completedLessons,
        totalLessons,
        lastWatched,
        lastDate
      };
    });

    // Build Activity Timeline (mix of progress and exams)
    let timeline = [];
    
    // Add completed lessons
    progress.filter(p => p.completed).forEach(p => {
      timeline.push({
        type: 'lesson',
        title: `Completed lesson: ${p.lessons?.title || 'Unknown'}`,
        icon: 'check_circle',
        color: '#3fb950', // green
        date: new Date(p.updated_at)
      });
    });

    // Add exam results
    exams.forEach(e => {
      timeline.push({
        type: 'exam',
        title: `Scored ${e.percentage}% in ${e.exams?.title || 'Exam'}`,
        icon: 'assignment',
        color: e.percentage >= 50 ? '#00D2FF' : '#f85149',
        date: new Date(e.completed_at)
      });
      if (e.xp_awarded > 0) {
        timeline.push({
          type: 'xp',
          title: `Earned ${e.xp_awarded} XP`,
          icon: 'star',
          color: '#FFD700',
          date: new Date(e.completed_at)
        });
      }
    });

    // Sort timeline desc
    timeline.sort((a, b) => b.date - a.date);
    // Take top 20
    timeline = timeline.slice(0, 20);

    return {
      courses: courseStats,
      exams: exams,
      timeline: timeline
    };
  }
}

// Initialize
window.AthenaeumParent = new AthenaeumParentService();
