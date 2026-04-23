CREATE DATABASE `policy_rag` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;


-- policy_rag.documents definition

CREATE TABLE `documents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_name` varchar(255) NOT NULL,
  `doc_category` varchar(100) DEFAULT NULL,
  `raw_text` longtext NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- policy_rag.eval_questions definition

CREATE TABLE `eval_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_type` varchar(50) DEFAULT NULL,
  `question_text` text NOT NULL,
  `expected_note` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- policy_rag.qa_logs definition

CREATE TABLE `qa_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question` text NOT NULL,
  `final_answer` longtext DEFAULT NULL,
  `source_chunk_ids` text DEFAULT NULL,
  `latency_ms` int(11) DEFAULT NULL,
  `estimated_tokens` int(11) DEFAULT NULL,
  `prompt_version` varchar(100) DEFAULT NULL,
  `retrieval_version` varchar(100) DEFAULT NULL,
  `model_version` varchar(100) DEFAULT NULL,
  `feedback_score` int(11) DEFAULT NULL,
  `feedback_comment` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- policy_rag.document_chunks definition

CREATE TABLE `document_chunks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document_id` int(11) NOT NULL,
  `chunk_order` int(11) NOT NULL,
  `chunk_text` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `document_id` (`document_id`),
  CONSTRAINT `document_chunks_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- policy_rag.eval_results definition

CREATE TABLE `eval_results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `eval_question_id` int(11) NOT NULL,
  `prompt_version` varchar(100) DEFAULT NULL,
  `retrieval_version` varchar(100) DEFAULT NULL,
  `model_version` varchar(100) DEFAULT NULL,
  `accuracy_score` int(11) DEFAULT NULL,
  `completeness_score` int(11) DEFAULT NULL,
  `grounding_score` int(11) DEFAULT NULL,
  `format_score` int(11) DEFAULT NULL,
  `total_score` int(11) DEFAULT NULL,
  `note` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `eval_question_id` (`eval_question_id`),
  CONSTRAINT `eval_results_ibfk_1` FOREIGN KEY (`eval_question_id`) REFERENCES `eval_questions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;