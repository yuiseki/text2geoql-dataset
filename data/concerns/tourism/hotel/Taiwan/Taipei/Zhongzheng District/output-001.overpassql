[out:json][timeout:30];
area["name:en"="Taipei"]->.outer;
area["name:en"="Zhongzheng District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
