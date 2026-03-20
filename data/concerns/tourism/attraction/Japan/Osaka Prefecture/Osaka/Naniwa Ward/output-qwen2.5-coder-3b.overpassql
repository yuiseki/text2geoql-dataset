[out:json][timeout:30];
area["name:en"="Osaka"][boundary=administrative]->.outer;
area["name:en"="Naniwa Ward"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
