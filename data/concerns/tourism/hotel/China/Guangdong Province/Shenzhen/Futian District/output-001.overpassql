[out:json][timeout:30000];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
