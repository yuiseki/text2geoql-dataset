[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Taisho Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
