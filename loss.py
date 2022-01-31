import torch
import torch.nn.functional as F
import math

from utils.utils import gamma2as


def diffusion_elbo(gamma_0, gamma_1, d_gamma_t,
                   x, noise, noise_hat):
    alpha_0, var_0 = gamma2as(gamma_0)
    alpha_1, var_1 = gamma2as(gamma_1)

    # prior loss KL(q(z_1|x) || p(z_1)))
    mu = alpha_1 * x
    prior_loss = 0.5 * torch.mean(var_1 + mu * mu - 1 - var_1.log())

    # recon loss E[-log p(x | z_0)]
    diff = (1 - alpha_0) * x
    l2 = diff * diff
    ll = -0.5 * (var_0.log() + l2 / var_0 + math.log(2 * math.pi)).mean()
    recon_loss = -ll

    extra_dict = {
        'kld': prior_loss.item(),
        'll': ll.item()
    }
    # diffusion loss
    diff = noise - noise_hat
    loss_T_raw = 0.5 * (d_gamma_t * (diff * diff).mean(1)
                        ) / d_gamma_t.shape[0]
    loss_T = loss_T_raw.sum()
    extra_dict['loss_T_raw'] = loss_T_raw.detach()
    extra_dict['loss_T'] = loss_T.item()

    loss = prior_loss + recon_loss + loss_T
    elbo = -loss
    extra_dict['elbo'] = elbo.item()
    return loss, extra_dict
