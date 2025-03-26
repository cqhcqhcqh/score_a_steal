from datetime import datetime
from src.model.models import SellerInfo

def build_seller_info(user_info, seller_id):
    if user_info:
            # data = user_info.get('data', {})
        base_info = user_info.get('baseInfo', {})
        encrypted_user_id = base_info.get('encryptedUserId', '')
        kc_user_id = base_info.get('kcUserId', '')
        # is_self = base_info.get('self', False)
        tags_json = base_info.get('tags', {})
        real_name_certification = tags_json.get('real_name_certification_77')
        xianyu_user_upgrade = tags_json.get('xianyu_user_upgrade')
        idle_zhima_zheng = tags_json.get('idle_zhima_zheng')
        tb_xianyu_user = tags_json.get('tb_xianyu_user')
        alibaba_idle_playboy = tags_json.get('alibaba_idle_playboy')

        tabs = user_info.get('tabs', {})
        item_count = tabs.get('itemCount', 0)
        rate = tabs.get('rate', '')

        module = user_info.get('module', {})
        base = module.get('base', {})
        display_name = base.get('displayName', '')
        avatar_url = base.get('avatar', {}).get('avatar', '')
        ip_location = base.get('ipLocation', '')
        ylz_tags = base.get('ylzTags', [])
        seller_level = 0
        seller_level_text = ''
        buyer_level = 0
        buyer_level_text = ''
        for ylz_tag in ylz_tags:
            if attributes := ylz_tag.get('attributes'):
                if attributes.get('role') == 'seller':
                    seller_level = attributes.get('level', 0)
                    seller_level_text = ylz_tag.get('text', '')
                elif attributes.get('role') == 'buyer':
                    buyer_level = attributes.get('level', 0)
                    buyer_level_text = ylz_tag.get('text', '')
        
        social = module.get('social', {})
        followers_count = social.get('followers', '0')
        following_count = social.get('following', '0') 
        attentionPrivacyProtected = True if social.get('attentionPrivacyProtected', "false") == "true" else False

        return SellerInfo(
                seller_id=seller_id,
                encrypted_user_id=encrypted_user_id,
                kc_user_id=kc_user_id,
                display_name=display_name,
                avatar_url=avatar_url,
                ip_location=ip_location,
                followers_count=followers_count,
                following_count=following_count,
                real_name_certification=real_name_certification,
                xianyu_user_upgrade=xianyu_user_upgrade,
                idle_zhima_zheng=idle_zhima_zheng,
                tb_xianyu_user=tb_xianyu_user,
                alibaba_idle_playboy=alibaba_idle_playboy,
                attentionPrivacyProtected=True if attentionPrivacyProtected == "true" else False,
                item_count=item_count,
                rate=rate,
                seller_level=seller_level,
                buyer_level=buyer_level,
                seller_level_text=seller_level_text,
                buyer_level_text=buyer_level_text,
                updated_at=datetime.now()
            )
