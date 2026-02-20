---
title: |
  Annex --- Supporting Figures and Tables \
  \vspace{0.2cm} \large Clinical Data Management for DM1 --- IGTP
author: "Gary Espitia"
date: "February 2026"
geometry: "margin=2cm"
fontsize: 10pt
documentclass: article
header-includes:
  - \usepackage{booktabs}
  - \usepackage{graphicx}
  - \usepackage{hyperref}
  - \usepackage{xcolor}
  - \usepackage{fancyhdr}
  - \usepackage{float}
  - \usepackage{caption}
  - \usepackage{parskip}
  - \renewcommand{\normalsize}{\fontsize{9}{10.8}\selectfont}
  - \renewcommand{\small}{\fontsize{8}{9.6}\selectfont}
  - \renewcommand{\footnotesize}{\fontsize{7}{8.4}\selectfont}
  - \normalsize
  - \pagestyle{fancy}
  - \fancyhead[L]{\footnotesize Annex --- Figures and Tables}
  - \fancyhead[R]{\footnotesize IGTP --- Clinical Data Manager}
  - \fancyfoot[C]{\thepage}
  - \definecolor{dm1blue}{HTML}{1565C0}
  - \hypersetup{colorlinks=true, linkcolor=dm1blue, urlcolor=dm1blue}
  - \setlength{\parskip}{4pt plus 1pt minus 1pt}
  - \captionsetup{font=small, labelfont=bf, skip=4pt}
---

\begin{center}
\small\textit{All artefacts are available at full resolution in the project repository:} \textbf{\url{https://github.com/stradichenko/task-ref-2026-14}}
\end{center}

\vspace{0.5cm}

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{data_flow/data_flow_diagram.png}
\caption{System Data Flow Diagram. Seven-layer architecture from patient mobile app and clinician portal through API services, Identity and Access Management (Keycloak), operational database, de-identification pipelines, OMOP CDM warehouse, to observability and audit logging. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/data_flow/data_flow_diagram.png}{data\_flow/data\_flow\_diagram.png}}}
\label{fig:dataflow}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{risk_matrix/risk_matrix.png}
\caption{Risk Likelihood--Impact Matrix. Four identified project risks (R1--R4) plotted by likelihood and impact severity. Colour coding indicates residual risk level after mitigation. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/risk_matrix/risk_matrix.png}{risk\_matrix/risk\_matrix.png}}}
\label{fig:riskmatrix}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{gantt/gantt.png}
\caption{Project Gantt Chart. Three-month timeline showing four overlapping workstreams: Foundation \& Design (Month 1), Configuration \& Implementation (Month 2), Validation \& Pilot (Month 3), and cross-cutting Governance. Key milestones are marked. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/gantt/gantt.png}{gantt/gantt.png}}}
\label{fig:gantt}
\end{figure}

\newpage

\begin{table}[H]
\centering
\caption{Role-Based Access Control (RBAC) Permission Matrix. Seven roles (System Administrator, Data Manager, Investigator, Site Coordinator, Data Engineer, Analyst/Researcher, External Auditor) mapped against 37 permissions across 11 categories. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/rbac/rbac_matrix.png}{rbac/rbac\_matrix.png}}}
\label{tab:rbac}
\includegraphics[width=\textwidth]{rbac/rbac_matrix.png}
\end{table}

\begin{table}[H]
\centering
\caption{Responsible--Accountable--Consulted--Informed (RACI) Responsibility Matrix. Task allocation across Clinical Data Manager, Development/Technical, Data Engineering, Legal/DPO, and Study Leadership roles for all major deliverables. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/raci/raci_matrix.png}{raci/raci\_matrix.png}}}
\label{tab:raci}
\includegraphics[width=\textwidth]{raci/raci_matrix.png}
\end{table}

\newpage

\begin{center}
\Large\textbf{Exploratory Statistical Analysis --- Selected Figures}
\end{center}

\vspace{0.3cm}

\noindent The figures below are excerpts from the full interactive exploratory analysis report, available at \textbf{\href{https://stradichenko.github.io/task-ref-2026-14/exploratory_analysis.html}{stradichenko.github.io --- Exploratory Analysis}}.

\vspace{0.3cm}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{small_exploratory_analysis/figures/demographics-1.png}
\caption{Demographic summary of the synthetic CDISC cohort. Distribution of age, sex, and race across treatment arms. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/small_exploratory_analysis/figures/demographics-1.png}{figures/demographics-1.png}}}
\label{fig:demographics}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{small_exploratory_analysis/figures/sbp-trajectories-1.png}
\caption{Longitudinal systolic blood pressure trajectories. Individual patient trajectories with LOESS smoothing by treatment arm, illustrating temporal trends and between-arm divergence. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/small_exploratory_analysis/figures/sbp-trajectories-1.png}{figures/sbp-trajectories-1.png}}}
\label{fig:sbp}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{small_exploratory_analysis/figures/lab-chg-baseline-1.png}
\caption{Change from baseline in laboratory parameters. Box plots showing the distribution of change-from-baseline values for key laboratory markers by treatment arm and visit. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/small_exploratory_analysis/figures/lab-chg-baseline-1.png}{figures/lab-chg-baseline-1.png}}}
\label{fig:labchange}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{small_exploratory_analysis/figures/km-plot-1.png}
\caption{Kaplan--Meier survival curves for time to first adverse event. Estimated event-free probability by treatment arm with 95\% confidence intervals and number-at-risk table. Source: \textbf{\href{https://github.com/stradichenko/task-ref-2026-14/blob/master/small_exploratory_analysis/figures/km-plot-1.png}{figures/km-plot-1.png}}}
\label{fig:km}
\end{figure}
