import OpenAI from "openai";

import * as fs from "fs";
import { promises as fsPromises } from "fs";
import * as readline from "readline/promises";
// const fs = require("fs");
// const readline = require("readline");

const openai = new OpenAI({
  apiKey: "YOUR_KEY",
});

async function read_jsonl() {
  const rl = readline.createInterface({
    input: fs.createReadStream("test/networkx_env/test_set_large.jsonl"),
    crlfDelay: Infinity,
  });

  const prompts = [];

  for await (const line of rl) {
    try {
      const jsonObject = JSON.parse(line);
      if (
        Array.isArray(jsonObject.messages) &&
        jsonObject.messages.length > 1
      ) {
        prompts.push(jsonObject.messages[1].content);
      }
    } catch (err) {
      console.error("Error parsing JSON:", err);
    }
  }

  return prompts;
}

async function get_inferences(modelName, outputFilename) {
  const prompts = await read_jsonl();
  const outputFile = modelName;
  await fsPromises.writeFile(outputFile, "");

  for (const prompt of prompts) {
    const completion = await openai.chat.completions.create({
      model: "ft:gpt-4o-mini-2024-07-18:lyw02:ety-100-001:B7NDJ7iP",
      messages: [
        {
          role: "system",
          content: `
You are a helpful linguist, especially expertise in English etymology.
The user will give you a piece of text that describes etymology of a word, you must output its structured etymology information in the given pattern.
Always output ONLY the structured information. No extra words.
Always remember, in side the output, etymology structure should be place inside <structure></structure> tag, and detailed content of each node should be placed inside <content></content> tag.
If the input is not relevant to etymology, you should output CANNOT_RECOGNISE.
`,
        },
        {
          role: "user",
          content: prompt,
        },
      ],
    });

    // const res_jsonl = []

    // console.log(completion.choices[0].message.content)

    const strucure_res =
      /<structure>([\s\S]*?)<\/structure>/.exec(
        completion.choices[0].message.content
      )?.[1] || "";
    await fsPromises.appendFile(
      outputFilename,
      JSON.stringify({
        messages: [
          {},
          {},
          {
            role: "assistant",
            content: `<structure>${strucure_res}</structure>`,
          },
        ],
      }) + "\n"
    );
    console.log(strucure_res);
  }
}

get_inferences(
  "inference_gpt_4o_mini_large.jsonl",
  "./test/networkx_env/inference_gpt_4o_mini_large.jsonl"
);
