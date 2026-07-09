from __future__ import annotations

import json
from pathlib import Path

REPORTS = [
    Path('/tmp/regression-standard.md'),
    Path('/tmp/regression-minimal.md'),
    Path('/tmp/regression-complete.md'),
    Path('/tmp/regression-remote-maintenance.md'),
    Path('/tmp/regression-address-constrained.md'),
    Path('/tmp/regression-multi-workshop.md'),
    Path('/tmp/regression-redundancy-demand.md'),
    Path('/tmp/regression-compound-conflict.md'),
    Path('/tmp/regression-conflict.md'),
    Path('/tmp/regression-dayawan-mes.md'),
    Path('/tmp/regression-formal-complete.md'),
    Path('/tmp/regression-formal-remote-maintenance.md'),
    Path('/tmp/regression-formal-address-constrained.md'),
    Path('/tmp/regression-formal-multi-workshop.md'),
    Path('/tmp/regression-formal-fmcs-from-framework.md'),
]

FORMAL_REPORTS = {
    '/tmp/regression-dayawan-mes.md',
    '/tmp/regression-formal-complete.md',
    '/tmp/regression-formal-remote-maintenance.md',
    '/tmp/regression-formal-address-constrained.md',
    '/tmp/regression-formal-multi-workshop.md',
    '/tmp/regression-formal-fmcs-from-framework.md',
}

REQUIRED_HEADINGS_DRAFT = [
    '## 项目概述与建设目标',
    '## 现状网络与调研结论',
    '## 设计依据与方法说明',
    '## 总体网络架构方案',
    '## ISA95 层级建模与系统协同结构',
    '## IEC62443 分区分域与安全边界设计',
    '## 网络拓扑与通信路径说明',
    '## IP 地址、VLAN 与子网规划',
    '## 关键设备与部署建议',
    '## 实施步骤与迁移建议',
    '## 风险、假设与待确认项',
    '## 结论与建议',
    '## 附录',
]

REQUIRED_HEADINGS_FORMAL = [
    '## 执行摘要',
    '## 项目概述',
    '## 现场调研与现状结论',
    '## 设计原则与技术路线',
    '## 需求与约束分析',
    '## 技术选择与方案比较',
    '## 总体网络架构方案',
    '## 网络分区与边界控制方案',
    '## 网络拓扑图',
    '## 地址、VLAN 与子网规划',
    '## 关键设备部署方案',
    '## 通信与运维接入方案',
    '## 实施方案与切换策略',
    '## 风险分析与待确认事项',
    '## 实施结论与定版条件',
    '## 附录',
]

BAD_PATTERNS = [
    '当前未标注',
    '方案层面宜项目目标',
    '实施工作宜按结合',
    '当前总体结构建议以依据现有',
    '基于安全目标和访问关系，以办公区、运维区、DMZ、控制区作为主要区域框架',
    '综合当前输入条件，方案宜以在完成现场复核与客户确认后',
]



def check_one(path: Path) -> dict:
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    if not path.exists() and (str(path).endswith('regression-conflict.md') or str(path).endswith('regression-dayawan-mes.md')):
        return {
            'report': str(path),
            'exists': False,
            'missing_headings': [],
            'bad_patterns': [],
            'repeated_phrases': [],
            'style_mismatch': [],
            'chapter_count': 0,
            'passes': True,
        }
    is_formal = str(path) in FORMAL_REPORTS or '面向客户交付的综合性网络方案版本' in text or '面向客户交付的正式方案版本' in text
    required_headings = REQUIRED_HEADINGS_FORMAL if is_formal else REQUIRED_HEADINGS_DRAFT
    missing_headings = [item for item in required_headings if item not in text]
    bad_patterns = [item for item in BAD_PATTERNS if item in text]
    chapter_count = text.count('## ')
    repeated_phrases = []
    for phrase in ['后续尚需优先闭环', '后续宜优先完成以下闭环事项']:
        if text.count(phrase) > 8:
            repeated_phrases.append(phrase)
    style_mismatch = []
    if is_formal:
        for forbidden in ['**本章目标**', '**输入来源**', '**规则主题**', '**适用前提**', '**闭环条件**', '## 输出前自检', '## 证据边界说明', '## 装配注记', '**已确认基础**', '**建议要点**', '**实施前提**', '**待确认事项**', '（来源：`', '**事实基础**', '**待客户确认**', '**基础对象摘要**']:
            if forbidden in text:
                style_mismatch.append(f'formal-forbidden-section:{forbidden}')
        for expected in ['**总体拓扑图**', '**重点边界拓扑图**', '```mermaid', '**访问控制矩阵摘要表**', '**地址与 VLAN 定版摘要表**', '**关键设备部署定版表**', 'AC-01', 'IP-01', 'EQ-01', 'CL-01']:
            if expected not in text:
                style_mismatch.append(f'formal-missing-delivery-table:{expected}')
        for awkward in ['建议实施路径按结合', '地址规划层面宜在现网形成地址复用的前提下', '结合当前项目目标与既有网络基础，建议总体架构以基于', '当前可确认的关键信息为', '结合项目已确认信息', '结合当前调研与现网资料', '方案总体上宜在完成现场复核与客户确认后，再固化', '总体建议按在完成现场复核与客户确认后，再固化', '需通过现场复核进一步落实', '完成确认后，方可进一步固化', '宜围绕', '建议采用', '建议划分', 'ISA95', 'IEC62443', '层级建模']:
            if awkward in text:
                style_mismatch.append(f'formal-awkward-phrase:{awkward}')
    min_chapters = 16 if is_formal else 15
    return {
        'report': str(path),
        'exists': path.exists(),
        'missing_headings': missing_headings,
        'bad_patterns': bad_patterns,
        'repeated_phrases': repeated_phrases,
        'style_mismatch': style_mismatch,
        'chapter_count': chapter_count,
        'passes': path.exists() and not missing_headings and not bad_patterns and not repeated_phrases and not style_mismatch and chapter_count >= min_chapters,
    }



def main() -> int:
    results = [check_one(path) for path in REPORTS]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item['passes'] for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())


if __name__ == '__main__':
    raise SystemExit(main())
