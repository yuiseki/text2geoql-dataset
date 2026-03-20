[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dongjak-gu"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
