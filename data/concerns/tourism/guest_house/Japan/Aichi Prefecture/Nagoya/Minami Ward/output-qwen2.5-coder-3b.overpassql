[out:json][timeout:30];
area["name:en"="Minami Ward"][boundary=administrative]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
