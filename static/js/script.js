function showSection(sectionId) {
    // مخفی کردن همه بخش‌ها
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('show');
        setTimeout(() => {
            section.classList.add('hidden');
        }, 300);
    });

    // پیدا کردن بخش انتخاب شده
    setTimeout(() => {
        const target = document.getElementById(sectionId);
        if (target) {
            target.classList.remove('hidden');

            // تعیین نوع انیمیشن بر اساس id
            if (sectionId === 'panel') {
                target.classList.add('panel-anim');
                target.classList.remove('info-anim');
            } else if (sectionId === 'info') {
                target.classList.add('info-anim');
                target.classList.remove('panel-anim');
            }

            // فعال کردن انیمیشن
            setTimeout(() => {
                target.classList.add('show');
            }, 10);
        }
    }, 300);
}
