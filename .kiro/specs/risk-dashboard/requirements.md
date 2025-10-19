# Requirements Document

## Introduction

The Risk Dashboard is a web-based application that aggregates data from multiple APIs to provide comprehensive risk assessments for DeFi protocols. The system transforms complex on-chain and off-chain data into clear, understandable risk scores with contextual explanations, enabling users to make informed decisions about DeFi protocol safety and reliability.

## Glossary

- **Risk Dashboard**: The web application system that displays protocol risk assessments
- **Protocol**: A DeFi (Decentralized Finance) smart contract system or platform
- **Risk Score**: A numerical value from 0-100 representing the overall safety assessment of a protocol
- **Risk Category**: One of four assessment dimensions (Security, Financial, Operational, Market)
- **API Aggregator**: The backend component that fetches and combines data from multiple external APIs
- **Protocol Card**: A visual UI component displaying summary information for a single protocol
- **Risk Radar Chart**: A visual representation showing risk scores across multiple categories
- **Traffic Light Indicator**: A color-coded system (Red/Yellow/Green) representing risk levels
- **MVP**: Minimum Viable Product - the initial prototype scope

## Requirements

### Requirement 1

**User Story:** As a DeFi investor, I want to view an overall risk score for protocols, so that I can quickly assess their safety level.

#### Acceptance Criteria

1. THE Risk Dashboard SHALL display a risk score between 0 and 100 for each protocol
2. WHEN a protocol's risk score is calculated, THE Risk Dashboard SHALL apply weighted contributions from four risk categories
3. THE Risk Dashboard SHALL assign 40% weight to Security category in the overall risk score calculation
4. THE Risk Dashboard SHALL assign 30% weight to Financial category in the overall risk score calculation
5. THE Risk Dashboard SHALL assign 20% weight to Operational category in the overall risk score calculation
6. THE Risk Dashboard SHALL assign 10% weight to Market category in the overall risk score calculation

### Requirement 2

**User Story:** As a DeFi investor, I want to see visual risk indicators, so that I can understand risk levels at a glance.

#### Acceptance Criteria

1. WHEN displaying a protocol, THE Risk Dashboard SHALL show a traffic light indicator based on the risk score
2. WHEN a protocol's risk score is 70 or above, THE Risk Dashboard SHALL display a green indicator
3. WHEN a protocol's risk score is between 40 and 69, THE Risk Dashboard SHALL display a yellow indicator
4. WHEN a protocol's risk score is below 40, THE Risk Dashboard SHALL display a red indicator
5. THE Risk Dashboard SHALL render a Protocol Card for each protocol containing the protocol name, overall risk score, and traffic light indicator

### Requirement 3

**User Story:** As a DeFi investor, I want to see detailed breakdowns of risk categories, so that I can understand specific risk factors.

#### Acceptance Criteria

1. WHEN a user selects a protocol, THE Risk Dashboard SHALL display individual scores for all four risk categories
2. THE Risk Dashboard SHALL render a Risk Radar Chart visualizing the four risk category scores
3. WHEN displaying risk category details, THE Risk Dashboard SHALL provide plain language explanations for each category
4. THE Risk Dashboard SHALL display specific risk factors contributing to each category score
5. THE Risk Dashboard SHALL provide actionable recommendations for each identified risk

### Requirement 4

**User Story:** As a DeFi investor, I want the dashboard to aggregate data from multiple sources, so that I receive comprehensive risk assessments.

#### Acceptance Criteria

1. THE API Aggregator SHALL fetch security data from at least one audit provider API
2. THE API Aggregator SHALL fetch market data from CoinGecko API
3. THE API Aggregator SHALL fetch TVL data from DeFi Llama API
4. THE API Aggregator SHALL fetch on-chain data from Etherscan API
5. WHEN an API request fails, THE API Aggregator SHALL log the error and continue processing with available data

### Requirement 5

**User Story:** As a DeFi investor, I want to view risk assessments for major Ethereum protocols, so that I can evaluate popular DeFi platforms.

#### Acceptance Criteria

1. THE Risk Dashboard SHALL support risk assessment for at least 5 Ethereum protocols in the MVP
2. THE Risk Dashboard SHALL include Aave protocol in the supported protocols list
3. THE Risk Dashboard SHALL include Uniswap protocol in the supported protocols list
4. THE Risk Dashboard SHALL include Compound protocol in the supported protocols list
5. THE Risk Dashboard SHALL display all supported protocols in a scrollable list view

### Requirement 6

**User Story:** As a DeFi investor, I want the dashboard to be responsive, so that I can access it from any device.

#### Acceptance Criteria

1. THE Risk Dashboard SHALL render correctly on desktop screens with width 1024 pixels or greater
2. THE Risk Dashboard SHALL render correctly on tablet screens with width between 768 and 1023 pixels
3. THE Risk Dashboard SHALL render correctly on mobile screens with width below 768 pixels
4. WHEN the viewport width changes, THE Risk Dashboard SHALL adjust layout to maintain readability
5. THE Risk Dashboard SHALL maintain all core functionality across all supported screen sizes

### Requirement 7

**User Story:** As a DeFi investor, I want to navigate between protocol list and detail views, so that I can explore protocols of interest.

#### Acceptance Criteria

1. WHEN a user clicks on a Protocol Card, THE Risk Dashboard SHALL navigate to the protocol detail view
2. THE Risk Dashboard SHALL display a back navigation control in the protocol detail view
3. WHEN a user activates the back navigation control, THE Risk Dashboard SHALL return to the protocol list view
4. THE Risk Dashboard SHALL preserve the scroll position when navigating back to the protocol list view
5. THE Risk Dashboard SHALL display the protocol name prominently in the detail view header

### Requirement 8

**User Story:** As a system administrator, I want the system to handle API failures gracefully, so that partial data is still useful to users.

#### Acceptance Criteria

1. WHEN an external API is unavailable, THE API Aggregator SHALL continue processing requests with remaining available APIs
2. WHEN data is missing for a risk category, THE Risk Dashboard SHALL display a "Data Unavailable" indicator for that category
3. THE API Aggregator SHALL implement a timeout of 10 seconds for each external API request
4. WHEN an API timeout occurs, THE API Aggregator SHALL log the timeout event with timestamp and API identifier
5. THE Risk Dashboard SHALL calculate risk scores using only available data when some APIs fail

### Requirement 9

**User Story:** As a DeFi investor, I want to understand the scoring methodology, so that I can trust the risk assessments.

#### Acceptance Criteria

1. THE Risk Dashboard SHALL provide a methodology explanation page accessible from the main navigation
2. THE Risk Dashboard SHALL document the weighting formula for overall risk score calculation
3. THE Risk Dashboard SHALL list all data sources used in risk assessment
4. THE Risk Dashboard SHALL explain the criteria for each risk category
5. THE Risk Dashboard SHALL describe the traffic light threshold values and their meanings

### Requirement 10

**User Story:** As a DeFi investor, I want risk data to be current, so that my decisions are based on up-to-date information.

#### Acceptance Criteria

1. THE API Aggregator SHALL refresh protocol data at intervals not exceeding 15 minutes
2. THE Risk Dashboard SHALL display the timestamp of the last data update for each protocol
3. WHEN displaying a protocol, THE Risk Dashboard SHALL show data age in human-readable format
4. THE API Aggregator SHALL cache API responses for 5 minutes to reduce external API load
5. WHEN cached data expires, THE API Aggregator SHALL fetch fresh data from external APIs
