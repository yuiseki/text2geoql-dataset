[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Mapo-gu"]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
