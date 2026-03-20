[out:json][timeout:30];
area["name:en"="Asahi Ward"][boundary=administrative]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["tourism"="camp_site"](area.inner)(area.outer);
);
out geom;
