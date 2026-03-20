[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
