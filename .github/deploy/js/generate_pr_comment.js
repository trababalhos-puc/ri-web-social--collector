module.exports = async ({github, context, core}) => {
  const fmtOutcome = core.getInput('fmt_outcome');
  const pr_exists = core.getInput('pr_exists');
  const initOutcome = core.getInput('init_outcome');
  const validateOutcome = core.getInput('validate_outcome');
  const planOutcome = core.getInput('plan_outcome');
  const destroyOutcome = core.getInput('destroy_outcome');
  const validateOutput = core.getInput('validate_stdout');
  const planOutput = core.getInput('plan_stdout');
  const destroyOutput = core.getInput('destroy_stdout');
  const infracostOutput = core.getInput('infracost_output');
  const infracostStatus = core.getInput('infracost_status');
  const actor = core.getInput('actor');
  const eventName = core.getInput('event_name');

  let output = `#### Terraform Format and Style 🖌 \`${infracostStatus}\`\n`;
  output += `#### Terraform Initialization ⚙️ \`${initOutcome}\`\n`;
  output += `#### Terraform Validation 🤖 \`${validateOutcome}\`\n`;
  output += `<details><summary>✅ Validation Output</summary>\n\n\`\`\`shell\n${validateOutput}\n\`\`\`\n</details>\n\n`;

  if (destroyOutcome === 'success') {
    output += `#### 💀 Terraform Destroy Results \`${destroyOutcome}\`\n`;
    output += `<details><summary>📄 Show Destroy Output</summary>\n\n\`\`\`shell\n${destroyOutput}\n\`\`\`\n</details>\n`;
  } else {
    output += `#### Terraform Plan 📖 \`${planOutcome}\`\n`;
    output += `<details><summary>📄 Show Plan Output</summary>\n\n\`\`\`shell\n${planOutput}\n\`\`\`\n</details>\n`;
  }

  output += `\n#### Infracost Breakdown 💰 \`${infracostStatus}\`\n`;
  output += `<details><summary>📄 Show Infracost Output</summary>\n\n\`\`\`shell\n${infracostOutput}\n\`\`\`\n</details><br>\n`;

  output += `\n*Pushed by: @${actor}, Action: \`${eventName}\`*`;
  await github.rest.issues.createComment({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body: output
  });

  console.log('PR comment created successfully');
  return output;
};
