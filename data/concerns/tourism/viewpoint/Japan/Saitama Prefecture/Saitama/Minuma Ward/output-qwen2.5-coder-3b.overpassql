[out:json][timeout:30];
area["name:en"="Saitama"][boundary=administrative]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
