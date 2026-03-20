[out:json][timeout:30];
area["name:en"="Kosovo"][boundary=administrative]->.outer;
area["name:en"="Pristina"]->.inner;
(
  nwr["tourism"="camp_site"](area.inner)(area.outer);
);
out geom;
