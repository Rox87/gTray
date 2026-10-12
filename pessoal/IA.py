import openai
import os
from pessoal.Escriba import registrador
from pessoal.config_manager import ConfigManager

class IA:
    def __init__(self, key, logger_from):
        global logger
        logger = logger_from
        self.config = ConfigManager()
        openai.api_key = key

    def change_key(self, key):
        openai.api_key = key

    def python_responder(self, prompt, mode='python', model_override=None):
        import re

        def detectar_caminho_arquivo(texto):
            padrao = r'@@([^@]+[\\/][^@]+)@'
            return re.findall(padrao, texto)

        caminhos_arquivos = detectar_caminho_arquivo(prompt)
        final_prompt = prompt

        for caminho in caminhos_arquivos:
            try:
                logger.info(f"Reading file: {caminho}")
                with open(caminho, 'r', encoding='utf-8') as file:
                    final_prompt += f'\n#{caminho}\n' + file.read()
            except Exception as e:
                logger.error(f"Error reading file {caminho}: {str(e)}")

        target_model = model_override or self.config.get_model(mode)
        try:
            response = openai.chat.completions.create(
                model=target_model,
                messages=[{"role": "system", "content": "seja extremamente breve e retorne apenas o nome entre ** seguido do bloco código python para cada arquivo da solução a seguir: " + final_prompt}]
            )
            coms = response.choices[0].message.content
            final_code = f'"""{final_prompt}"""\n'

            padrao = r'\*\*(.*?)\*\*\n```(.*?)\n(.*?)```'
            matches = re.findall(padrao, coms, re.DOTALL)

            for match in matches:
                filename, lang, bloco = match
                logger.info(f"Generated code for: {filename}")
                final_code += f'{lang} - {filename}\n{bloco}'

            return final_code

        except Exception as e:
            logger.error(f"Error in AI response: {str(e)}")
            raise

    def responder(self, prompt, cmd="", mode=None, model_override=None):
        messages = [
            {"role": "system", "content": cmd},
            {"role": "user", "content": prompt}
        ]
        response = ""
        retry = self.config.get_retry_attempts()
        target_model = model_override or self.config.get_model(mode)

        while response == "" and retry > 0:
            retry -= 1
            try:
                response = openai.chat.completions.create(
                    model=target_model,
                    messages=messages
                )
                break
            except Exception as e:
                logger.error(f"AI request failed (attempts left: {retry}): {str(e)}")
                if retry == 0:
                    raise

        resposta = response.choices[0].message.content
        logger.info(f'Response received: {resposta[:100]}...')
        return resposta