from djongo import models

class CompanyInfo(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'pep_company_info'
