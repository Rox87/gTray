import os
import re
from openai import OpenAI, AuthenticationError, PermissionDeniedError, NotFoundError, BadRequestError
from pessoal.Escriba import registrador
from pessoal.config_manager import ConfigManager

class IA:
    def __init__(self, key, logger_from, base_url=None):
        global logger
        logger = logger_from
        self.config = ConfigManager()
        self.key = key or ""
        self.base_url = base_url
        self._init_client()

    def _init_client(self):
        kwargs = {"api_key": self.key if self.key else "dummy_key"}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self.client = OpenAI(**kwargs)

    def change_key(self, key, base_url=None):
        changed = False
        if key is not None and key != self.key:
            self.key = key
            changed = True
        if base_url != self.base_url:
            self.base_url = base_url
            changed = True
        if changed or not hasattr(self, 'client'):
            self._init_client()

    def python_responder(self, prompt, mode='python', model_override=None):
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
            response = self.client.chat.completions.create(
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

        except (AuthenticationError, PermissionDeniedError) as auth_err:
            logger.error(f"AI authentication error (verifique chave/provedor): {str(auth_err)}")
            raise
        except (BadRequestError, NotFoundError) as req_err:
            logger.error(f"AI request error (verifique modelo '{target_model}'): {str(req_err)}")
            raise
        except Exception as e:
            logger.error(f"Error in AI response: {str(e)}")
            raise

    def responder(self, prompt, cmd="", mode=None, model_override=None):
        messages = [
            {"role": "system", "content": cmd},
            {"role": "user", "content": prompt}
        ]
        response = None
        retry = self.config.get_retry_attempts()
        target_model = model_override or self.config.get_model(mode)

        while response is None and retry > 0:
            retry -= 1
            try:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages
                )
                break
            except (AuthenticationError, PermissionDeniedError) as auth_err:
                logger.error(f"AI authentication error (verifique a chave de API e provedor): {str(auth_err)}")
                raise
            except (BadRequestError, NotFoundError) as req_err:
                logger.error(f"AI request error (verifique o modelo '{target_model}'): {str(req_err)}")
                raise
            except Exception as e:
                logger.error(f"AI request failed (attempts left: {retry}): {str(e)}")
                if retry == 0:
                    raise

        if not response or not response.choices:
            raise RuntimeError("Nenhuma resposta recebida da IA.")

        resposta = response.choices[0].message.content
        logger.info(f'Response received: {resposta[:100]}...')
        return resposta