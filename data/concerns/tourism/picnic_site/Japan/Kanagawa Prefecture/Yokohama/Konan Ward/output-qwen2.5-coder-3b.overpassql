[out:json][timeout:30];
area["name:en"="Yokohama"][boundary=administrative]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
