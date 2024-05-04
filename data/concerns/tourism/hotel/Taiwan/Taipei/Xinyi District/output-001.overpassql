[out:json][timeout:30000];
area["name:en"="Taipei"]->.outer;
area["name:en"="Xinyi District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
