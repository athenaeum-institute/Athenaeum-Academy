// ─────────────────────────────────────────────────────────────
// Supabase Service Class for Mock Exams
// Contains all database logic required for mock-exam.html
// ─────────────────────────────────────────────────────────────

class AthenaeumExamService {
  constructor() {
    this.client = window.supabaseClient;
  }

  async getStudentId() {
    const { data: { session } } = await this.client.auth.getSession();
    return session?.user?.id || null;
  }

  async getProfile() {
    const sid = await this.getStudentId();
    if (!sid) return null;
    const { data, error } = await this.client.from('profiles').select('plan_type, xp').eq('id', sid).single();
    if (error) throw error;
    return data;
  }

  // Fetch all exams for courses the student is enrolled in
  async getAvailableExams() {
    const sid = await this.getStudentId();
    if (!sid) return [];

    // 1. Get enrolled courses
    const { data: enrollments } = await this.client.from('enrollments').select('course_id').eq('student_id', sid);
    const courseIds = enrollments ? enrollments.map(e => e.course_id) : [];

    // 2. Fetch all published exams
    const { data: exams, error } = await this.client.from('exams')
      .select('*, courses(title)')
      .eq('is_published', true)
      .order('created_at', { ascending: false });
    
    if (error) throw error;

    // 3. Get best scores for these exams
    const { data: results } = await this.client.from('exam_results')
      .select('exam_id, percentage')
      .eq('student_id', sid);

    const bestScores = {};
    if (results) {
      results.forEach(r => {
        if (!bestScores[r.exam_id] || r.percentage > bestScores[r.exam_id]) {
          bestScores[r.exam_id] = r.percentage;
        }
      });
    }

    return exams.map(e => ({
      ...e,
      isEnrolled: courseIds.includes(e.course_id),
      bestScore: bestScores[e.id] || null
    }));
  }

  // Check if student can take exam today (Free trial = max 2)
  async canTakeExamToday() {
    const sid = await this.getStudentId();
    const profile = await this.getProfile();
    if (!profile) return false;
    if (profile.plan_type === 'paid') return true; // Unlimited

    // Check today's attempts
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const { count, error } = await this.client.from('exam_results')
      .select('*', { count: 'exact', head: true })
      .eq('student_id', sid)
      .gte('completed_at', today.toISOString());
    
    if (error) throw error;
    return (count || 0) < 2;
  }

  async getExamDetails(examId) {
    const { data: exam, error } = await this.client.from('exams')
      .select('*, courses(title)')
      .eq('id', examId)
      .single();
    if (error) throw error;

    const { data: questions, error: qErr } = await this.client.from('exam_questions')
      .select('*')
      .eq('exam_id', examId)
      .order('order_index', { ascending: true });
    if (qErr) throw qErr;

    return { exam, questions };
  }

  async submitExamResult(examId, score, totalMarks, percentage, timeTaken, answers, xpAwarded) {
    const sid = await this.getStudentId();
    if (!sid) throw new Error("Not logged in");

    // 1. Save Result
    const { data, error } = await this.client.from('exam_results').insert([{
      student_id: sid,
      exam_id: examId,
      score,
      total_marks: totalMarks,
      percentage,
      time_taken_minutes: timeTaken,
      answers,
      xp_awarded: xpAwarded
    }]).select().single();
    
    if (error) throw error;

    // 2. Add XP
    if (xpAwarded > 0) {
      const { error: xpErr } = await this.client.rpc('add_student_xp', { amount: xpAwarded });
      if (xpErr) console.error("Failed to add XP", xpErr);
    }

    return data;
  }
}

// Initialize on window
window.AthenaeumExam = new AthenaeumExamService();
