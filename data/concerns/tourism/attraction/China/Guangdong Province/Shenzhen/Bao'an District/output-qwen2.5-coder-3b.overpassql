[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Bao'an District"]->.inner;
(
  nwr["tourism"](area.inner)(area.outer);
);
out geom;
