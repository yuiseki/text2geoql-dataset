[out:json][timeout:30];
area["name:en"="Nagoya"][boundary=administrative]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
